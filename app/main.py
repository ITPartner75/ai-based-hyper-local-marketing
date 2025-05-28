from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base  # This includes your models
from app.api.v1.auth import router as auth_router
from app.api.v1.business import router as business_router


app = FastAPI()
origins = [
    "http://localhost:5173",
    "http://192.168.77.8:5173"
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

