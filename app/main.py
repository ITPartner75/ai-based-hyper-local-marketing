import uvicorn
from fastapi import FastAPI
from db.session import engine
from db.base import Base  # This includes your models
from api.v1.auth import router as auth_router

app = FastAPI()

# ✅ Create tables on startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# ✅ Include routes
app.include_router(auth_router, prefix="/api/v1/auth")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")

