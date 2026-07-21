# Publish EdgeBoard as a real website

## What the Blueprint creates

The included `render.yaml` creates:

- `edgeboard-mlb`: the public FastAPI website
- `edgeboard-mlb-db`: managed PostgreSQL storage
- `edgeboard-mlb-refresh`: a cron worker that refreshes every 30 minutes
- a generated `SITE_PASSWORD` and `CRON_SECRET`
- a prompt for your private `ODDS_API_KEY`

## Publish steps

1. Put this folder in a GitHub repository.
2. Sign in to Render.
3. Choose **New → Blueprint**.
4. Connect the GitHub repository.
5. Render reads `render.yaml` automatically.
6. Enter your Odds API key when prompted for `ODDS_API_KEY`.
7. Approve the services and database.
8. After deployment, open the web service's `onrender.com` URL.
9. In the web service environment settings, reveal/copy `SITE_PASSWORD` and use it when the site prompts you.

## Costs

The production Blueprint intentionally uses paid starter compute and a basic PostgreSQL database. The cron service also has a minimum monthly charge. Check Render's current pricing screen before approving the Blueprint.

## Custom domain

After the site is live:

1. Open the Render web service.
2. Choose **Settings → Custom Domains**.
3. Add your purchased domain.
4. Add the DNS records Render provides at your domain registrar.

Render provisions and renews HTTPS automatically after verification.

## Updating the website

Push updates to the connected GitHub branch. Render automatically rebuilds and deploys the latest version.
