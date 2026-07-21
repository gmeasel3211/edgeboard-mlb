from __future__ import annotations

import asyncio
import json
import secrets
from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from .config import get_settings
from .db import SessionLocal, init_db
from .models import Game, Projection, Quote, Recommendation
from .services.pipeline import Pipeline

settings = get_settings()
pipeline = Pipeline()
scheduler = AsyncIOScheduler(timezone=settings.timezone)
security = HTTPBasic(auto_error=False)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.filters["from_json"] = lambda value: json.loads(value) if value else []
templates.env.filters["market_name"] = lambda value: {
    "h2h": "Moneyline", "spreads": "Run line", "totals": "Total"
}.get(value, value.replace("_", " ").title())
templates.env.filters["local_time"] = lambda value: value.astimezone(ZoneInfo(settings.timezone)).strftime("%b %d, %I:%M %p ET") if value else "—"


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


async def refresh_job(force_official: bool = False):
    db = SessionLocal()
    try:
        return await pipeline.refresh(db, force_official=force_official)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if settings.run_internal_scheduler:
        scheduler.add_job(
            refresh_job,
            "interval",
            minutes=settings.refresh_minutes,
            id="refresh",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        scheduler.start()
    if settings.refresh_on_startup:
        asyncio.create_task(refresh_job())
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


def record_summary(db: Session) -> dict:
    graded = db.scalars(select(Recommendation).where(
        Recommendation.official.is_(True), Recommendation.status == "graded"
    )).all()
    wins = sum(1 for x in graded if x.result == "win")
    losses = sum(1 for x in graded if x.result == "loss")
    pushes = sum(1 for x in graded if x.result == "push")
    units_risked = sum(x.units for x in graded)
    profit = sum(x.profit_units or 0 for x in graded)
    clvs = [x.clv for x in graded if x.clv is not None]
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


def common_context(request: Request, db: Session) -> dict:
    summary = record_summary(db)
    last_refresh = db.scalar(select(func.max(Quote.fetched_at)))
    return {
        "request": request,
        "app_name": settings.app_name,
        "demo_mode": not bool(settings.odds_api_key),
        "unit_value": settings.bankroll * settings.unit_percent,
        "model_version": settings.model_version,
        "last_refresh": last_refresh,
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
    games = {g.id: g for g in db.scalars(select(Game).where(Game.game_date == today)).all()}
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
    return templates.TemplateResponse("index.html", context)


@app.get("/history", response_class=HTMLResponse, dependencies=[Depends(require_site_access)])
def history(request: Request, db: Session = Depends(get_db)):
    picks = db.scalars(
        select(Recommendation)
        .where(Recommendation.official.is_(True))
        .order_by(desc(Recommendation.pick_date), desc(Recommendation.created_at))
        .limit(500)
    ).all()
    games = {g.id: g for g in db.scalars(select(Game)).all()}
    context = common_context(request, db)
    context.update({"picks": picks, "games": games, "page": "history"})
    return templates.TemplateResponse("history.html", context)


@app.get("/api/status", dependencies=[Depends(require_site_access)])
def api_status(db: Session = Depends(get_db)):
    return {
        "app": settings.app_name,
        "environment": settings.environment,
        "model_version": settings.model_version,
        "live_odds_enabled": bool(settings.odds_api_key),
        "scheduler_enabled": settings.run_internal_scheduler,
        "refresh_minutes": settings.refresh_minutes,
        "last_quote_refresh": db.scalar(select(func.max(Quote.fetched_at))),
        "games": db.scalar(select(func.count()).select_from(Game)) or 0,
        "official_picks": db.scalar(
            select(func.count()).select_from(Recommendation).where(Recommendation.official.is_(True))
        ) or 0,
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
    return JSONResponse(await refresh_job(force_official=force_official))


@app.post("/api/admin/refresh")
async def admin_refresh(
    authorization: str | None = Header(default=None),
    force_official: bool = False,
):
    expected = f"Bearer {settings.cron_secret}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid authorization")
    return await refresh_job(force_official=force_official)


@app.get("/api/picks", dependencies=[Depends(require_site_access)])
def api_picks(pick_date: date | None = None, db: Session = Depends(get_db)):
    target = pick_date or datetime.now(ZoneInfo(settings.timezone)).date()
    picks = db.scalars(
        select(Recommendation)
        .where(Recommendation.pick_date == target, Recommendation.official.is_(True))
        .order_by(desc(Recommendation.expected_value))
    ).all()
    return [{
        "date": p.pick_date.isoformat(),
        "game_id": p.game_id,
        "market": p.market,
        "selection": p.selection,
        "line": p.line,
        "bookmaker": p.bookmaker,
        "odds": p.odds,
        "model_probability": p.model_prob,
        "market_probability": p.market_prob,
        "fair_odds": p.fair_odds,
        "edge": p.edge,
        "expected_value": p.expected_value,
        "units": p.units,
        "grade": p.grade,
        "status": p.status,
        "result": p.result,
        "profit_units": p.profit_units,
        "closing_odds": p.closing_odds,
        "clv": p.clv,
        "explanation": json.loads(p.explanation_json),
    } for p in picks]
