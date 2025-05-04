from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base  # This includes your models
from app.api.v1.auth import router as auth_router

app = FastAPI()

# ✅ Create tables on startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# ✅ Include routes
app.include_router(auth_router, prefix="/api/v1/auth")

