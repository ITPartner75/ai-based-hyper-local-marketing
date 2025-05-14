import uvicorn
from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base  # This includes your models
from app.api.v1.auth import router as auth_router
from app.api.v1.business import router as business_router


app = FastAPI()

# ✅ Create tables on startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# ✅ Include routes
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(business_router, prefix="/api/v1", tags=["Business"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")

