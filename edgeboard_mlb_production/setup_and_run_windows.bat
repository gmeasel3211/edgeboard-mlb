@echo off
setlocal
cd /d %~dp0
if not exist .env copy .env.example .env >nul
if not exist .venv (
  py -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Open .env and add ODDS_API_KEY before relying on live picks.
echo Starting EdgeBoard at http://localhost:8000
start http://localhost:8000
uvicorn app.main:app --host 127.0.0.1 --port 8000
