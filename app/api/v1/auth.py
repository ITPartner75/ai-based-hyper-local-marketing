from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from crud.otp import check_if_mobile_number_verified
from core.security import create_access_token, create_refresh_token, decode_token, get_password_hash
from schemas.otp import SendOTPRequest, VerifyOTPRequest, Token
from schemas.user import UserLogin, UserCreate, UserLogout
from services.auth_service import send_otp, verify_otp_and_signup, verify_otp, login_user, logout_user
from crud import user as user_crud
from db.base import get_db


router = APIRouter()

@router.post("/send-otp")
def send_otp_route(request: SendOTPRequest, db: Session = Depends(get_db)):
    return send_otp(db, request)

@router.post("/verify-otp")
def verify_otp_route(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    try:
        # token = verify_otp_and_signup(db, request)
        # return {"detail": "OTP verification successful.", "access_token": token, "token_type": "bearer"}
        # tokens = verify_otp_and_signup(db, request)
        if verify_otp(db, request):
            return {
                "detail": "OTP verification successful.",
                # "access_token": tokens["access_token"],
                # "refresh_token": tokens["refresh_token"],
                # "token_type": "bearer"
            }
        else:
            return {
                "detail": "Invalid OTP.",
                # "access_token": tokens["access_token"],
                # "refresh_token": tokens["refresh_token"],
                # "token_type": "bearer"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login_route(request: UserLogin, db: Session = Depends(get_db)):
    try:
        tokens = login_user(db, request)
        return {
            "detail": "Login successful.",
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer"
        }
        # token = login_user(db, request)
        # return {"detail": "Login successful.", "access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/create-credentials")
def create_credentials(data: UserCreate, db: Session = Depends(get_db)):
    verified = check_if_mobile_number_verified(db, data.mobile_number)
    if not verified:
        raise HTTPException(status_code=404, detail="Mobile not found or OTP not verified")

    # if user.hashed_password:
    #     raise HTTPException(status_code=400, detail="Credentials already set")

    hashed_pw = get_password_hash(data.password)
    user = user_crud.create_user(db, hashed_pw, data)

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return {"detail": "Credentials created successfully.", "access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token")
async def refresh_token_route(request: Request):
    body = await request.json()
    refresh_token = body.get("refresh_token")
    
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_token = create_access_token({"sub": payload["sub"], "role": payload.get("role")})
    return {"access_token": new_token, "token_type": "bearer"}


@router.post("/logout")
def logout(data: UserLogout, db: Session = Depends(get_db)):
    # Frontend should delete access + refresh tokens
    # user = user_crud.get_user_by_username(db, data.username)
    if logout_user(db, data):
        return {"detail": "Logged out successfully."}
    else:
        return {"detail": "Log Out Failed.."}
