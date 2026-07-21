APP_NAME=EdgeBoard MLB
ENVIRONMENT=development
TIMEZONE=America/New_York
DATABASE_URL=sqlite:///./edgeboard.db

# Required for live FanDuel + DraftKings odds:
ODDS_API_KEY=

# Optional. The app otherwise uses MLB's public web-data endpoints.
SPORTRADAR_API_KEY=

# Security for the manual refresh / cron endpoint:
CRON_SECRET=replace-with-a-long-random-string
SITE_PASSWORD=choose-a-private-dashboard-password

# Automatic refresh:
RUN_INTERNAL_SCHEDULER=true
REFRESH_ON_STARTUP=true
REFRESH_MINUTES=30
DAILY_PICK_HOUR_ET=8
MAX_OFFICIAL_PICKS=3

# Model / staking:
MODEL_VERSION=2.1.0
BANKROLL=1000
UNIT_PERCENT=0.01
KELLY_FRACTION=0.25
MAX_BET_UNITS=2.0
MAX_DAILY_UNITS=5.0
MIN_EDGE=0.025
MIN_EV=0.025
MIN_DATA_QUALITY=65

# Set true only to preview the interface without a live odds key.
DEMO_MODE=true
