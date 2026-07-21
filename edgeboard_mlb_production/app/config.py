from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EdgeBoard MLB"
    environment: str = "development"
    timezone: str = "America/New_York"
    database_url: str = "sqlite:///./edgeboard.db"

    odds_api_key: str = ""
    sportradar_api_key: str = ""
    cron_secret: str = "change-me"
    site_password: str = ""

    run_internal_scheduler: bool = True
    refresh_on_startup: bool = True
    refresh_minutes: int = 30
    daily_pick_hour_et: int = 8
    max_official_picks: int = 3

    model_version: str = "2.1.0"
    bankroll: float = 1000.0
    unit_percent: float = 0.01
    kelly_fraction: float = 0.25
    max_bet_units: float = 2.0
    max_daily_units: float = 5.0
    min_edge: float = 0.025
    min_ev: float = 0.025
    min_data_quality: int = 65

    demo_mode: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
