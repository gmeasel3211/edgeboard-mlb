EDGEBOARD MLB — PROFESSIONAL ADMIN CENTER + SITE REDESIGN
=========================================================

WHAT THIS PACKAGE ADDS
----------------------
• A professional, responsive dashboard redesign
• A private /admin operations center
• One-click standard model refresh
• One-click force_official=True card regeneration
• One-click grading of completed official picks
• CSV export of today's official card
• Database-backed model settings that can be edited in the browser
• Refresh/action status messages
• Persistent system audit logs
• Mobile navigation and improved history search
• A refresh lock that prevents two refreshes from running at once

FILES INCLUDED
--------------
Replace these existing files in your repository:

1. edgeboard_mlb_production/app/main.py
2. edgeboard_mlb_production/app/models.py
3. edgeboard_mlb_production/app/templates/base.html
4. edgeboard_mlb_production/app/templates/index.html
5. edgeboard_mlb_production/app/templates/history.html
6. edgeboard_mlb_production/app/static/styles.css
7. edgeboard_mlb_production/app/static/app.js

Add this new file:

8. edgeboard_mlb_production/app/templates/admin.html

GITHUB INSTALLATION
-------------------
1. Unzip this package on your computer.
2. Open your gmeasel3211/edgeboard-mlb repository in GitHub.
3. Navigate to each matching folder and replace the seven existing files.
4. Add admin.html inside app/templates.
5. Commit all eight files together with a message such as:

   Add professional admin center and dashboard redesign

RENDER DEPLOYMENT
-----------------
1. Open the edgeboard-mlb service in Render.
2. Choose Manual Deploy.
3. Choose Clear build cache & deploy.
4. Wait for the deploy to finish.
5. Open:

   https://edgeboard-mlb.onrender.com/admin

SECURITY — IMPORTANT
--------------------
The Admin Center uses the same Basic Authentication as the private dashboard.
Set SITE_PASSWORD in Render before sharing the website URL.

Username: edgeboard
Password: the value of SITE_PASSWORD

The one-click browser controls do not expose CRON_SECRET.
The existing Bearer-token API refresh endpoint remains available for cron use.

DATABASE NOTES
--------------
The app creates two new tables automatically during startup:

• runtime_settings
• system_events

No manual migration is required because init_db() already runs SQLAlchemy
Base.metadata.create_all().

Runtime settings persist in the configured application database. If Render is
using PostgreSQL, they survive deploys and restarts. If the service is using an
ephemeral SQLite database without a persistent disk, all database content can
be lost when the service restarts; that is a Render storage limitation rather
than an Admin Center limitation.

USING THE ADMIN CENTER
----------------------
Standard refresh:
Updates schedule, scores, odds, projections and candidates while preserving the
existing official card.

Regenerate official picks:
Runs the full pipeline with force_official=True. Pending official picks for
today may be returned to candidate status and replaced.

Grade pending picks:
Settles official picks whose games have final scores loaded.

Strategy settings:
Settings are saved to the database and applied immediately to future model
runs. After changing thresholds or staking rules, regenerate today's card if
you want the new settings applied to today's official selections.

ROLLBACK
--------
Keep a copy of the current files before replacing them. To undo the redesign,
restore the prior versions and redeploy. The two new database tables can remain;
older application code will simply ignore them.
