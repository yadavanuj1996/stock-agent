import os
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import bcrypt
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    from config import load_config
    load_config()

from main import run as orchestrator_run

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
serializer = URLSafeTimedSerializer(SECRET_KEY)
COOKIE_NAME = "session"
COOKIE_MAX_AGE = 86400 * 7

CHARTS_DIR = Path(__file__).parent / "static" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

_executor = ThreadPoolExecutor(max_workers=4)


def _get_session(request: Request) -> dict | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        return serializer.loads(token, max_age=COOKIE_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def _require_auth(request: Request) -> dict:
    session = _get_session(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session


class LoginRequest(BaseModel):
    username: str
    password: str


class AnalyseRequest(BaseModel):
    query: str


@app.post("/api/login")
async def login(body: LoginRequest, response: Response):
    username = os.environ.get("DASHBOARD_USERNAME")
    password_hash = os.environ.get("DASHBOARD_PASSWORD")
    if not username or not password_hash:
        raise HTTPException(status_code=500, detail="Credentials not configured")
    if body.username != username or not bcrypt.checkpw(body.password.encode(), password_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = serializer.dumps({"username": body.username})
    response.set_cookie(
        COOKIE_NAME, token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return {"authenticated": True}


@app.post("/api/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"authenticated": False}


@app.get("/api/me")
async def me(request: Request):
    session = _get_session(request)
    return {"authenticated": session is not None}


@app.post("/api/analyse")
async def analyse(body: AnalyseRequest, session: dict = Depends(_require_auth)):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(_executor, orchestrator_run, body.query)

    chart_filenames = []
    for chart_path in result.get("charts", []):
        src = Path(chart_path)
        chart_filenames.append(src.name)

    return {
        "response": result["response"],
        "charts": chart_filenames,
        "ticker": result["ticker"],
    }


app.mount("/api/charts", StaticFiles(directory=str(CHARTS_DIR)), name="charts")

_frontend_dir = Path(__file__).parent / "static" / "frontend"
if _frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
