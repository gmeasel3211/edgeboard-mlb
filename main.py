from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="EdgeBoard MLB")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>EdgeBoard MLB</title>
        </head>
        <body style="font-family: Arial; padding: 40px;">
            <h1>EdgeBoard MLB</h1>
            <p>The website is successfully running on Render.</p>
        </body>
    </html>
    """
