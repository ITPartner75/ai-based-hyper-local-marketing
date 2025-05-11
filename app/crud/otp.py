# app/crud/otp.py
from sqlalchemy.orm import Session
from models.otp_attempt import OTPAttempt
import datetime

def create_otp_attempt(db: Session, mobile_number: str, otp_code: str):
    attempt = OTPAttempt(mobile_number=mobile_number, otp_code=otp_code)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt

def verify_otp(db: Session, mobile_number: str, otp_code: str):
    recent = db.query(OTPAttempt).filter(
        OTPAttempt.mobile_number == mobile_number,
        OTPAttempt.otp_code == otp_code,
        OTPAttempt.is_verified == False,
        OTPAttempt.created_at >= datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    ).first()
    if recent:
        recent.is_verified = True
        db.commit()
        return True
    return False


def check_if_mobile_number_verified(db: Session, mobile_number: str):
    verified = db.query(OTPAttempt).filter(
        OTPAttempt.mobile_number == mobile_number,
        OTPAttempt.is_verified == True,
        OTPAttempt.created_at >= datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
    ).first()
    if verified:
        return True
    return False