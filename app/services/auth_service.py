import random, string
from app.schemas.otp import SendOTPRequest, VerifyOTPRequest
from app.schemas.user import UserLogin
from app.crud import user as user_crud, otp as otp_crud
from app.core.security import get_password_hash, verify_password, create_access_token
from app.external.sms_call_service import send_sms_or_call


def generate_credentials():
    username = "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return username, password

def send_otp(db, request: SendOTPRequest):
    otp = str(random.randint(100000, 999999))
    message = f"Dear%20User%2C%20Your%20login%20OTP%20is%20{otp}.%20Regards%2C%20TRACERT%20SERVICES%20PRIVATE%20LIMITED."
    otp_crud.create_otp_attempt(db, request.mobile_number, otp)
    send_sms_or_call(request.mobile_number, message)
    return {"message": "OTP sent"}

def verify_otp_and_signup(db, request: VerifyOTPRequest):
    if not otp_crud.verify_otp(db, request.mobile_number, request.otp_code):
        raise Exception("Invalid OTP")
    user = user_crud.get_user_by_mobile(db, request.mobile_number) or user_crud.create_user(db, request.mobile_number)
    username, password = generate_credentials()
    hashed = get_password_hash(password)
    user = user_crud.update_user_credentials(db, user, username, hashed)
    # send_sms_or_call(request.mobile_number, f"Username: {username}, Password: {password}")
    return create_access_token({"sub": str(user.id), "role": user.role})

def login_user(db, login: UserLogin):
    user = user_crud.get_user_by_username(db, login.username)
    if not user or not verify_password(login.password, user.hashed_password):
        raise Exception("Invalid credentials")
    return create_access_token({"sub": str(user.id), "role": user.role})
