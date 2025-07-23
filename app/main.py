from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from alembic.config import Config
from alembic import command
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base  # This includes your models
from app.api.v1.auth import router as auth_router
from app.api.v1.business import router as business_router
from pathlib import Path
import spacy
import subprocess
import sys


BASE_DIR = Path(__file__).resolve().parent.parent

def download_spacy_model():
    try:
        spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading 'en_core_web_sm' model...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

def run_migrations():
    print(str(BASE_DIR / "alembic.ini"))
    alembic_cfg = Config(str(BASE_DIR / "alembic.ini"))
    print(alembic_cfg.__dict__)
    command.upgrade(alembic_cfg, "head")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    download_spacy_model()
    run_migrations()
    yield
    # Shutdown logic (optional)

app = FastAPI()
origins = [
    "http://localhost:5173",
    "http://0.0.0.0",
    "http://14.99.81.62:5173",
    "http://192.168.77.8:5173",
    "https://glokai.netlify.app",
    "https://glok-ai.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Create tables on startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# ✅ Include routes
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(business_router, prefix="/api/v1", tags=["Business"])
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

