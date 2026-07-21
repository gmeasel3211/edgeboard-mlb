from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    game_date: Mapped[date] = mapped_column(Date, index=True)
    commence_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    provider_game_id: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    mlb_game_pk: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)

    away_team: Mapped[str] = mapped_column(String(80))
    home_team: Mapped[str] = mapped_column(String(80))
    away_team_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    home_team_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_pitcher: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    home_pitcher: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    away_pitcher_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    home_pitcher_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    venue: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(30), default="scheduled")
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weather_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Quote(Base):
    __tablename__ = "quotes"
    __table_args__ = (
        UniqueConstraint(
            "game_id", "bookmaker", "market", "selection", "line", "fetched_at",
            name="uq_quote_snapshot"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(String(120), index=True)
    bookmaker: Mapped[str] = mapped_column(String(30))
    market: Mapped[str] = mapped_column(String(30))
    selection: Mapped[str] = mapped_column(String(100))
    line: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price: Mapped[int] = mapped_column(Integer)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class Projection(Base):
    __tablename__ = "projections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(String(120), index=True)
    model_version: Mapped[str] = mapped_column(String(30))
    away_runs: Mapped[float] = mapped_column(Float)
    home_runs: Mapped[float] = mapped_column(Float)
    away_win_prob: Mapped[float] = mapped_column(Float)
    home_win_prob: Mapped[float] = mapped_column(Float)
    data_quality: Mapped[int] = mapped_column(Integer)
    reasons_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pick_date: Mapped[date] = mapped_column(Date, index=True)
    game_id: Mapped[str] = mapped_column(String(120), index=True)
    model_version: Mapped[str] = mapped_column(String(30))

    market: Mapped[str] = mapped_column(String(30))
    selection: Mapped[str] = mapped_column(String(100))
    line: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bookmaker: Mapped[str] = mapped_column(String(30))
    odds: Mapped[int] = mapped_column(Integer)

    model_prob: Mapped[float] = mapped_column(Float)
    market_prob: Mapped[float] = mapped_column(Float)
    fair_odds: Mapped[int] = mapped_column(Integer)
    edge: Mapped[float] = mapped_column(Float)
    expected_value: Mapped[float] = mapped_column(Float)
    units: Mapped[float] = mapped_column(Float)
    grade: Mapped[str] = mapped_column(String(10))
    data_quality: Mapped[int] = mapped_column(Integer)
    explanation_json: Mapped[str] = mapped_column(Text)

    official: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    result: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    profit_units: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    closing_odds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    clv: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    graded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
