from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.crud.otp import check_if_mobile_number_verified
from app.core.security import create_access_token, create_refresh_token, decode_token, get_password_hash
from app.schemas.otp import SendOTPRequest, VerifyOTPRequest, Token
from app.schemas.user import UserLogin, UserCreate, UserLogout
from app.services.auth_service import send_otp, verify_otp_and_signup, verify_otp, login_user, logout_user
from app.crud import user as user_crud
from app.db.base import get_db
from app.exceptions.auth import UserNotFound, InvalidCredentials


router = APIRouter()

@router.post("/send-otp")
def send_otp_route(request: SendOTPRequest, db: Session = Depends(get_db)):
    try:
        if send_otp(db, request):
            return {"status_code": 200, "detail": "OTP sent successfully."}
        else:
            return {"status_code": 400, "detail": "Failed to sent OTP."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-otp")
def verify_otp_route(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    try:
        if verify_otp(db, request):
            return {
                "status_code": 200,
                "detail": "OTP verification successful.",
            }
        else:
            return {
                "status_code": 403,
                "detail": "Invalid OTP.",
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login_route(request: UserLogin, db: Session = Depends(get_db)):
    try:
        tokens = login_user(db, request)
        return {
            "status_code": 200,
            "detail": "Login successful.",
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer"
        }
    except (UserNotFound, InvalidCredentials, Exception) as e:
        if hasattr(e, "status_code") and hasattr(e, "msg"):
            raise HTTPException(status_code=e.status_code, detail=e.msg)
        else:
            raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/signup")
def signup_route(data: UserCreate, db: Session = Depends(get_db)):
    verified = check_if_mobile_number_verified(db, data.mobile_number)
    if not verified:
        raise HTTPException(status_code=404, detail="Mobile not found or OTP not verified")

    hashed_pw = get_password_hash(data.password)
    user = user_crud.create_user(db, hashed_pw, data)
    try:
        access_token = create_access_token({"mobile_number": user.mobile_number, "role": user.role})
        refresh_token = create_refresh_token({"mobile_number": user.mobile_number, "role": user.role})
        return {"status_code": 200, "detail": "User created successfully.", "access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except:
        user_crud.delete_user(db, user)
        return {"status_code": 400, "detail": "Failed to create user."}



@router.post("/refresh-token")
async def refresh_token_route(request: Request):
    body = await request.json()
    refresh_token = body.get("refresh_token")
    
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid refresh token.")

    new_token = create_access_token({"mobile": payload["mobile"], "name": payload.get("name")})
    return {"status_code": 200, "detail": "New access token generated successfully.", "access_token": new_token, "token_type": "bearer"}


@router.post("/logout")
def logout(data: UserLogout, db: Session = Depends(get_db)):
    # Frontend should delete access + refresh tokens
    # user = user_crud.get_user_by_username(db, data.username)
    try:
        if logout_user(db, data):
            return {"status_code": 200, "detail": "Logged out successfully."}
        else:
            return {"status_code": 400, "detail": "Log Out Failed.."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
