from __future__ import annotations

import asyncio
import csv
import io
import json
import secrets
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import delete, desc, func, select
from sqlalchemy.orm import Session

from .config import Settings, get_settings
from .db import SessionLocal, init_db
from .models import Game, Projection, Quote, Recommendation, RuntimeSetting, SystemEvent
from .services.pipeline import Pipeline

settings = get_settings()
pipeline = Pipeline()
scheduler = AsyncIOScheduler(timezone=settings.timezone)
security = HTTPBasic(auto_error=False)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
refresh_lock = asyncio.Lock()

refresh_state: dict[str, Any] = {
    "running": False,
    "source": None,
    "force_official": False,
    "started_at": None,
    "finished_at": None,
    "result": None,
    "error": None,
}

SETTING_SPECS: dict[str, dict[str, Any]] = {
    "bankroll": {
        "label": "Bankroll",
        "description": "Dollar bankroll used to calculate the displayed value of one unit.",
        "type": float,
        "minimum": 1.0,
        "maximum": 10_000_000.0,
        "step": 50.0,
        "group": "Bankroll and staking",
        "prefix": "$",
    },
    "unit_percent": {
        "label": "Unit size",
        "description": "Percentage of bankroll represented by one unit.",
        "type": float,
        "minimum": 0.001,
        "maximum": 0.25,
        "step": 0.001,
        "group": "Bankroll and staking",
        "format": "percent",
    },
    "kelly_fraction": {
        "label": "Kelly fraction",
        "description": "Fraction of full Kelly used when sizing qualified bets.",
        "type": float,
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
        "group": "Bankroll and staking",
        "format": "percent",
    },
    "max_bet_units": {
        "label": "Maximum units per bet",
        "description": "Hard cap for the recommended stake on one wager.",
        "type": float,
        "minimum": 0.1,
        "maximum": 10.0,
        "step": 0.05,
        "group": "Bankroll and staking",
    },
    "max_daily_units": {
        "label": "Maximum daily exposure",
        "description": "Total unit cap across the official card.",
        "type": float,
        "minimum": 0.1,
        "maximum": 50.0,
        "step": 0.1,
        "group": "Bankroll and staking",
    },
    "min_edge": {
        "label": "Minimum model edge",
        "description": "Minimum model probability advantage required for a candidate.",
        "type": float,
        "minimum": 0.0,
        "maximum": 0.5,
        "step": 0.005,
        "group": "Qualification thresholds",
        "format": "percent",
    },
    "min_ev": {
        "label": "Minimum expected value",
        "description": "Minimum expected return required before a market qualifies.",
        "type": float,
        "minimum": 0.0,
        "maximum": 0.5,
        "step": 0.005,
        "group": "Qualification thresholds",
        "format": "percent",
    },
    "min_data_quality": {
        "label": "Minimum data quality",
        "description": "Lowest acceptable projection data-quality score.",
        "type": int,
        "minimum": 0,
        "maximum": 100,
        "step": 1,
        "group": "Qualification thresholds",
    },
    "max_official_picks": {
        "label": "Maximum official picks",
        "description": "Maximum number of tracked wagers on the daily official card.",
        "type": int,
        "minimum": 1,
        "maximum": 20,
        "step": 1,
        "group": "Automation",
    },
    "daily_pick_hour_et": {
        "label": "Automatic card hour (ET)",
        "description": "Eastern Time hour when a normal refresh may create the daily card.",
        "type": int,
        "minimum": 0,
        "maximum": 23,
        "step": 1,
        "group": "Automation",
    },
    "refresh_minutes": {
        "label": "Refresh interval",
        "description": "Minutes between internal scheduler refreshes.",
        "type": int,
        "minimum": 5,
        "maximum": 1440,
        "step": 5,
        "group": "Automation",
        "suffix": "min",
    },
}


def _format_local_time(value: datetime | None) -> str:
    if not value:
        return "—"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(ZoneInfo(settings.timezone)).strftime("%b %d, %I:%M %p ET")


templates.env.filters["from_json"] = lambda value: json.loads(value) if value else []
templates.env.filters["market_name"] = lambda value: {
    "h2h": "Moneyline",
    "spreads": "Run line",
    "totals": "Total",
}.get(value, value.replace("_", " ").title())
templates.env.filters["local_time"] = _format_local_time


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_site_access(credentials: HTTPBasicCredentials | None = Depends(security)) -> bool:
    """Protect the private dashboard when SITE_PASSWORD is configured."""
    if not settings.site_password:
        return True
    valid_user = credentials is not None and secrets.compare_digest(credentials.username, "edgeboard")
    valid_password = credentials is not None and secrets.compare_digest(
        credentials.password.encode("utf-8"), settings.site_password.encode("utf-8")
    )
    if not (valid_user and valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Dashboard authentication required",
            headers={"WWW-Authenticate": 'Basic realm="EdgeBoard MLB"'},
        )
    return True


def _cast_setting(key: str, raw_value: Any) -> int | float:
    spec = SETTING_SPECS.get(key)
    if not spec:
        raise ValueError(f"Unknown setting: {key}")
    try:
        value = spec["type"](raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{spec['label']} must be a valid number.") from exc
    if value < spec["minimum"] or value > spec["maximum"]:
        raise ValueError(
            f"{spec['label']} must be between {spec['minimum']} and {spec['maximum']}."
        )
    return value


def apply_runtime_settings(db: Session) -> None:
    """Apply database-backed overrides to the shared Settings instance."""
    for row in db.scalars(select(RuntimeSetting)).all():
        if row.key not in SETTING_SPECS:
            continue
        try:
            setattr(settings, row.key, _cast_setting(row.key, row.value))
        except ValueError:
            continue


def settings_for_template(db: Session) -> list[dict[str, Any]]:
    saved_keys = set(db.scalars(select(RuntimeSetting.key)).all())
    rows: list[dict[str, Any]] = []
    for key, spec in SETTING_SPECS.items():
        rows.append({
            "key": key,
            "label": spec["label"],
            "description": spec["description"],
            "group": spec["group"],
            "value": getattr(settings, key),
            "minimum": spec["minimum"],
            "maximum": spec["maximum"],
            "step": spec["step"],
            "format": spec.get("format"),
            "prefix": spec.get("prefix"),
            "suffix": spec.get("suffix"),
            "overridden": key in saved_keys,
        })
    return rows


def write_system_event(
    event_type: str,
    source: str,
    event_status: str,
    summary: str,
    details: dict[str, Any] | None = None,
) -> None:
    db = SessionLocal()
    try:
        db.add(SystemEvent(
            event_type=event_type,
            source=source,
            status=event_status,
            summary=summary,
            details_json=json.dumps(details or {}, default=str),
        ))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def configure_refresh_schedule() -> None:
    if not settings.run_internal_scheduler:
        return
    job = scheduler.get_job("refresh")
    if job:
        scheduler.reschedule_job("refresh", trigger="interval", minutes=settings.refresh_minutes)
    else:
        scheduler.add_job(
            refresh_job,
            "interval",
            minutes=settings.refresh_minutes,
            id="refresh",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )


async def refresh_job(force_official: bool = False, source: str = "scheduler") -> dict[str, Any]:
    async with refresh_lock:
        started_at = datetime.now(timezone.utc)
        refresh_state.update({
            "running": True,
            "source": source,
            "force_official": force_official,
            "started_at": started_at.isoformat(),
            "finished_at": None,
            "result": None,
            "error": None,
        })
        db = SessionLocal()
        try:
            result = await pipeline.refresh(db, force_official=force_official)
            finished_at = datetime.now(timezone.utc)
            refresh_state.update({
                "running": False,
                "finished_at": finished_at.isoformat(),
                "result": result,
                "error": None,
            })
            summary = (
                f"Loaded {result.get('games', 0)} games, created "
                f"{result.get('candidates', 0)} candidates and "
                f"{result.get('official_created', 0)} official picks."
            )
            write_system_event("refresh", source, "success", summary, result)
            return result
        except Exception as exc:
            db.rollback()
            finished_at = datetime.now(timezone.utc)
            refresh_state.update({
                "running": False,
                "finished_at": finished_at.isoformat(),
                "result": None,
                "error": str(exc),
            })
            write_system_event("refresh", source, "error", str(exc), {"force_official": force_official})
            raise
        finally:
            db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        apply_runtime_settings(db)
    finally:
        db.close()

    if settings.run_internal_scheduler:
        configure_refresh_schedule()
        scheduler.start()
    if settings.refresh_on_startup:
        asyncio.create_task(refresh_job(source="startup"))
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)


app = FastAPI(
    title=settings.app_name,
    version=settings.model_version,
    lifespan=lifespan,
    docs_url=None if settings.environment == "production" else "/docs",
    redoc_url=None,
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def record_summary(db: Session) -> dict[str, Any]:
    graded = db.scalars(select(Recommendation).where(
        Recommendation.official.is_(True), Recommendation.status == "graded"
    )).all()
    wins = sum(1 for item in graded if item.result == "win")
    losses = sum(1 for item in graded if item.result == "loss")
    pushes = sum(1 for item in graded if item.result == "push")
    units_risked = sum(item.units for item in graded)
    profit = sum(item.profit_units or 0 for item in graded)
    clvs = [item.clv for item in graded if item.clv is not None]
    return {
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "units_risked": units_risked,
        "profit": profit,
        "roi": profit / units_risked if units_risked else 0.0,
        "avg_clv": sum(clvs) / len(clvs) if clvs else None,
        "graded_count": len(graded),
    }


def common_context(request: Request, db: Session) -> dict[str, Any]:
    summary = record_summary(db)
    last_refresh = db.scalar(select(func.max(Quote.fetched_at)))
    return {
        "request": request,
        "app_name": settings.app_name,
        "demo_mode": not bool(settings.odds_api_key),
        "unit_value": settings.bankroll * settings.unit_percent,
        "model_version": settings.model_version,
        "last_refresh": last_refresh,
        "environment": settings.environment,
        "scheduler_enabled": settings.run_internal_scheduler,
        "site_secured": bool(settings.site_password),
        **summary,
    }


@app.get("/healthz")
def healthz(db: Session = Depends(get_db)):
    db.scalar(select(func.count()).select_from(Game))
    return {"status": "ok", "model_version": settings.model_version}


@app.get("/", response_class=HTMLResponse, dependencies=[Depends(require_site_access)])
def dashboard(request: Request, db: Session = Depends(get_db)):
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    official = db.scalars(
        select(Recommendation)
        .where(Recommendation.pick_date == today, Recommendation.official.is_(True))
        .order_by(desc(Recommendation.expected_value))
    ).all()
    candidates = db.scalars(
        select(Recommendation)
        .where(
            Recommendation.pick_date == today,
            Recommendation.official.is_(False),
            Recommendation.status == "candidate",
        )
        .order_by(desc(Recommendation.expected_value))
        .limit(15)
    ).all()
    games = {game.id: game for game in db.scalars(select(Game).where(Game.game_date == today)).all()}
    latest_projection: dict[str, Projection] = {}
    for projection in db.scalars(select(Projection).order_by(desc(Projection.created_at))).all():
        latest_projection.setdefault(projection.game_id, projection)
    recent = db.scalars(
        select(Recommendation)
        .where(Recommendation.official.is_(True), Recommendation.status == "graded")
        .order_by(desc(Recommendation.graded_at))
        .limit(12)
    ).all()
    context = common_context(request, db)
    context.update({
        "today": today,
        "official": official,
        "candidates": candidates,
        "games": games,
        "projections": latest_projection,
        "recent": recent,
        "page": "dashboard",
    })
    return templates.TemplateResponse(request=request, name="index.html", context=context)


@app.get("/history", response_class=HTMLResponse, dependencies=[Depends(require_site_access)])
def history(request: Request, db: Session = Depends(get_db)):
    picks = db.scalars(
        select(Recommendation)
        .where(Recommendation.official.is_(True))
        .order_by(desc(Recommendation.pick_date), desc(Recommendation.created_at))
        .limit(500)
    ).all()
    games = {game.id: game for game in db.scalars(select(Game)).all()}
    context = common_context(request, db)
    context.update({"picks": picks, "games": games, "page": "history"})
    return templates.TemplateResponse(request=request, name="history.html", context=context)


@app.get("/admin", response_class=HTMLResponse, dependencies=[Depends(require_site_access)])
def admin_page(request: Request, db: Session = Depends(get_db)):
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    recent_events = db.scalars(
        select(SystemEvent).order_by(desc(SystemEvent.created_at)).limit(20)
    ).all()
    counts = {
        "today_games": db.scalar(
            select(func.count()).select_from(Game).where(Game.game_date == today)
        ) or 0,
        "today_official": db.scalar(
            select(func.count()).select_from(Recommendation).where(
                Recommendation.pick_date == today,
                Recommendation.official.is_(True),
            )
        ) or 0,
        "today_candidates": db.scalar(
            select(func.count()).select_from(Recommendation).where(
                Recommendation.pick_date == today,
                Recommendation.official.is_(False),
                Recommendation.status == "candidate",
            )
        ) or 0,
        "pending": db.scalar(
            select(func.count()).select_from(Recommendation).where(
                Recommendation.official.is_(True),
                Recommendation.status == "pending",
            )
        ) or 0,
        "quotes": db.scalar(select(func.count()).select_from(Quote)) or 0,
        "projections": db.scalar(select(func.count()).select_from(Projection)) or 0,
    }
    context = common_context(request, db)
    context.update({
        "page": "admin",
        "today": today,
        "counts": counts,
        "runtime_settings": settings_for_template(db),
        "setting_groups": ["Bankroll and staking", "Qualification thresholds", "Automation"],
        "recent_events": recent_events,
        "refresh_state": refresh_state.copy(),
    })
    return templates.TemplateResponse(request=request, name="admin.html", context=context)


@app.post("/admin/actions/refresh", dependencies=[Depends(require_site_access)])
async def admin_action_refresh(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    action = payload.get("action", "refresh")

    if action == "grade":
        db = SessionLocal()
        try:
            graded = pipeline.grade_pending(db)
            result = {"graded": graded}
            write_system_event(
                "grade",
                "admin",
                "success",
                f"Graded {graded} completed official pick{'s' if graded != 1 else ''}.",
                result,
            )
            return JSONResponse(result)
        except Exception as exc:
            write_system_event("grade", "admin", "error", str(exc))
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        finally:
            db.close()

    if action not in {"refresh", "force_official"}:
        raise HTTPException(status_code=400, detail="Unknown admin action")
    if refresh_lock.locked():
        raise HTTPException(status_code=409, detail="A refresh is already running.")

    try:
        return JSONResponse(await refresh_job(
            force_official=action == "force_official",
            source="admin",
        ))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/admin/actions/status", dependencies=[Depends(require_site_access)])
def admin_action_status():
    return refresh_state.copy()


@app.post("/admin/settings", dependencies=[Depends(require_site_access)])
async def save_admin_settings(request: Request):
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid settings payload") from exc

    values = payload.get("settings", payload)
    if not isinstance(values, dict):
        raise HTTPException(status_code=400, detail="Settings must be an object")

    validated: dict[str, int | float] = {}
    errors: list[str] = []
    for key, raw_value in values.items():
        if key not in SETTING_SPECS:
            continue
        try:
            validated[key] = _cast_setting(key, raw_value)
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        raise HTTPException(status_code=422, detail=errors)
    if not validated:
        raise HTTPException(status_code=400, detail="No recognized settings were provided")

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        for key, value in validated.items():
            row = db.get(RuntimeSetting, key)
            if row is None:
                row = RuntimeSetting(key=key, value=str(value), updated_at=now)
                db.add(row)
            else:
                row.value = str(value)
                row.updated_at = now
        db.commit()
        apply_runtime_settings(db)
        configure_refresh_schedule()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not save settings: {exc}") from exc
    finally:
        db.close()

    write_system_event(
        "settings",
        "admin",
        "success",
        f"Updated {len(validated)} runtime setting{'s' if len(validated) != 1 else ''}.",
        validated,
    )
    return {
        "saved": validated,
        "message": "Settings saved. Regenerate the card to apply them to today's recommendations.",
    }


@app.post("/admin/settings/reset", dependencies=[Depends(require_site_access)])
def reset_admin_settings():
    db = SessionLocal()
    try:
        db.execute(delete(RuntimeSetting))
        db.commit()
        deployment_settings = Settings()
        for key in SETTING_SPECS:
            setattr(settings, key, getattr(deployment_settings, key))
        configure_refresh_schedule()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not reset settings: {exc}") from exc
    finally:
        db.close()

    write_system_event(
        "settings",
        "admin",
        "success",
        "Reset runtime settings to Render environment values.",
    )
    return {"message": "Runtime settings were reset to the deployment environment values."}


@app.get("/admin/export/today.csv", dependencies=[Depends(require_site_access)])
def export_today_csv(db: Session = Depends(get_db)):
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    picks = db.scalars(
        select(Recommendation)
        .where(Recommendation.pick_date == today, Recommendation.official.is_(True))
        .order_by(desc(Recommendation.expected_value))
    ).all()
    games = {game.id: game for game in db.scalars(select(Game).where(Game.game_date == today)).all()}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "date", "matchup", "market", "selection", "line", "bookmaker", "odds",
        "model_probability", "market_probability", "fair_odds", "edge",
        "expected_value", "units", "grade", "status",
    ])
    for pick in picks:
        game = games.get(pick.game_id)
        matchup = f"{game.away_team} @ {game.home_team}" if game else pick.game_id
        writer.writerow([
            pick.pick_date,
            matchup,
            pick.market,
            pick.selection,
            pick.line,
            pick.bookmaker,
            pick.odds,
            pick.model_prob,
            pick.market_prob,
            pick.fair_odds,
            pick.edge,
            pick.expected_value,
            pick.units,
            pick.grade,
            pick.status,
        ])
    output.seek(0)
    headers = {"Content-Disposition": f'attachment; filename="edgeboard-{today}.csv"'}
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers=headers)


@app.get("/api/status", dependencies=[Depends(require_site_access)])
def api_status(db: Session = Depends(get_db)):
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    return {
        "app": settings.app_name,
        "environment": settings.environment,
        "model_version": settings.model_version,
        "live_odds_enabled": bool(settings.odds_api_key),
        "scheduler_enabled": settings.run_internal_scheduler,
        "refresh_minutes": settings.refresh_minutes,
        "last_quote_refresh": db.scalar(select(func.max(Quote.fetched_at))),
        "games": db.scalar(select(func.count()).select_from(Game)) or 0,
        "today_games": db.scalar(
            select(func.count()).select_from(Game).where(Game.game_date == today)
        ) or 0,
        "official_picks": db.scalar(
            select(func.count()).select_from(Recommendation).where(Recommendation.official.is_(True))
        ) or 0,
        "refresh_state": refresh_state.copy(),
        "record": record_summary(db),
    }


@app.post("/api/cron/refresh")
async def cron_refresh(
    authorization: str | None = Header(default=None),
    force_official: bool = False,
):
    expected = f"Bearer {settings.cron_secret}"
    if not settings.cron_secret or authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid cron authorization")
    if refresh_lock.locked():
        raise HTTPException(status_code=409, detail="A refresh is already running.")
    return JSONResponse(await refresh_job(force_official=force_official, source="cron"))


@app.post("/api/admin/refresh")
async def admin_refresh(
    authorization: str | None = Header(default=None),
    force_official: bool = False,
):
    expected = f"Bearer {settings.cron_secret}"
    if not settings.cron_secret or authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid authorization")
    if refresh_lock.locked():
        raise HTTPException(status_code=409, detail="A refresh is already running.")
    return JSONResponse(await refresh_job(force_official=force_official, source="api"))


@app.get("/api/picks", dependencies=[Depends(require_site_access)])
def api_picks(pick_date: date | None = None, db: Session = Depends(get_db)):
    target = pick_date or datetime.now(ZoneInfo(settings.timezone)).date()
    picks = db.scalars(
        select(Recommendation)
        .where(Recommendation.pick_date == target, Recommendation.official.is_(True))
        .order_by(desc(Recommendation.expected_value))
    ).all()
    return [{
        "date": pick.pick_date.isoformat(),
        "game_id": pick.game_id,
        "market": pick.market,
        "selection": pick.selection,
        "line": pick.line,
        "bookmaker": pick.bookmaker,
        "odds": pick.odds,
        "model_probability": pick.model_prob,
        "market_probability": pick.market_prob,
        "fair_odds": pick.fair_odds,
        "edge": pick.edge,
        "expected_value": pick.expected_value,
        "units": pick.units,
        "grade": pick.grade,
        "status": pick.status,
        "result": pick.result,
        "profit_units": pick.profit_units,
        "closing_odds": pick.closing_odds,
        "clv": pick.clv,
        "explanation": json.loads(pick.explanation_json),
    } for pick in picks]
