# EdgeBoard MLB — Production Website

EdgeBoard is a private, automated MLB betting-model website for **FanDuel and DraftKings only**.

## Included website features

- Responsive dashboard for phone and desktop
- Private password protection
- Today's official model card
- Game-level score and win-probability projections
- Qualifying watchlist
- Permanent official-pick history
- Automated W-L-P, units, ROI and CLV tracking
- FanDuel and DraftKings moneylines, run lines and totals
- No-vig market probabilities, fair odds, edge, expected value and fractional-Kelly stakes
- Automatic final-score grading
- JSON endpoints for later connecting notifications or a mobile app

## Production architecture

The included `render.yaml` creates:

1. A public FastAPI web service
2. A managed PostgreSQL database
3. A separate cron worker that refreshes the model every 30 minutes
4. Generated private credentials for the dashboard and admin endpoints

The cron worker is deliberately separate from the website process, so data updates do not depend on someone opening the site.

## Publish it

Read **[DEPLOY_RENDER.md](DEPLOY_RENDER.md)**.

At a high level:

1. Upload this folder to a GitHub repository.
2. In Render, create a new Blueprint from that repository.
3. Enter the Odds API key when Render prompts for `ODDS_API_KEY`.
4. Approve the web service, database and cron worker.
5. Open the generated `onrender.com` address.

Render reads the included infrastructure file and configures the services automatically.

## Private login

In production, Render generates `SITE_PASSWORD` automatically.

- Username: `edgeboard`
- Password: the value of `SITE_PASSWORD` in the web service's environment settings

## Local preview

### Windows

Double-click:

```text
setup_and_run_windows.bat
```

### macOS or Linux

```bash
./setup_and_run_mac_linux.sh
```

For live prices, create `.env` from `.env.example`, add `ODDS_API_KEY`, and set `DEMO_MODE=false`.

## Data sources

- Live sportsbook prices: The Odds API, filtered to FanDuel and DraftKings
- MLB schedule, probable pitchers, standings and results: MLB web-data endpoints
- Weather: National Weather Service hourly forecasts

The MLB public adapter is best-effort. A licensed MLB data feed is recommended before treating the application as a commercial product.

## Important modeling note

This is a transparent quantitative MVP, not a guarantee of profit. Collect a meaningful out-of-sample record and evaluate calibration and closing-line value before increasing stake sizes. The application analyzes prices and tracks recommendations; it never places wagers.
