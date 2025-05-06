from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.security import create_access_token, get_password_hash
from schemas.otp import SendOTPRequest, VerifyOTPRequest, Token
from schemas.user import UserLogin, UserCreate
from services.auth_service import send_otp, verify_otp_and_signup, login_user
from crud import user as user_crud
from db.base import get_db


router = APIRouter()

@router.post("/send-otp")
def send_otp_route(request: SendOTPRequest, db: Session = Depends(get_db)):
    return send_otp(db, request)

@router.post("/verify-otp", response_model=Token)
def verify_otp_route(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    try:
        token = verify_otp_and_signup(db, request)
        return {"detail": "OTP verification successful.", "access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login_route(request: UserLogin, db: Session = Depends(get_db)):
    try:
        token = login_user(db, request)
        return {"detail": "Login successful.", "access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/create-credentials")
def create_credentials(data: UserCreate, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_mobile(db, data.mobile_number)
    if not user:
        raise HTTPException(status_code=404, detail="Mobile not found or OTP not verified")

    # if user.hashed_password:
    #     raise HTTPException(status_code=400, detail="Credentials already set")

    hashed_pw = get_password_hash(data.password)
    user_crud.update_user_credentials(db, user, data.username, hashed_pw)

    token = create_access_token({"sub": user.username})
    return {"detail": "Credentials created successfully.", "access_token": token, "token_type": "bearer"}