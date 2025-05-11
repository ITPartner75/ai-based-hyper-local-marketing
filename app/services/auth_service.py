import random, string
from schemas.otp import SendOTPRequest, VerifyOTPRequest
from constants.access_history import AccessStatus
from schemas.user import UserLogin, UserLogout
from crud import user as user_crud, otp as otp_crud, access_history
from core.security import create_refresh_token, get_password_hash, verify_password, create_access_token
from external.sms_call_service import send_sms_or_call


def generate_credentials():
    username = "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return username, password

def send_otp(db, request: SendOTPRequest):
    otp = str(random.randint(100000, 999999))
    message = f"Dear User,\n Your login OTP is {otp}.\n Regards,\n CLICKSEEK DIGITAL."
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
    access_data = {"sub": str(user.id), "role": user.role}
    # return create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": create_access_token(access_data),
        "refresh_token": create_refresh_token(access_data)
    }

def verify_otp(db, request: VerifyOTPRequest):
    if not otp_crud.verify_otp(db, request.mobile_number, request.otp_code):
        raise Exception("Invalid OTP")
    return True


def login_user(db, login: UserLogin):
    user = user_crud.get_user_by_username(db, login.username)
    login_hashed = get_password_hash(login.password)
    if not user or not verify_password(login.password, user.hashed_password):
        access_history.create_access_history(db, login.username, login_hashed, AccessStatus.FAILED.value)
        raise Exception("Invalid credentials")
    access_history.create_access_history(db, login.username, login_hashed, AccessStatus.SUCCESSFUL.value)
    access_data = {"sub": str(user.id), "role": user.role}
    # return create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": create_access_token(access_data),
        "refresh_token": create_refresh_token(access_data)
    }

def logout_user(db, login: UserLogout):
    try:
        user = user_crud.get_user_by_username(db, login.username)
        # login_hashed = get_password_hash(user.password)
        if not user:
            return False
        access_history.create_access_history(db, login.username, None, AccessStatus.LOGOUT.value)
        return True
    except Exception as e:
        print(e)
        return False

def send_username_password(db, mobile_number: str, username: str):
    message = f"Dear User,\n Your username is {username}.\n Regards,\n CLICKSEEK DIGITAL."
    send_sms_or_call(mobile_number, message)
    return {"message": "Username sent"}