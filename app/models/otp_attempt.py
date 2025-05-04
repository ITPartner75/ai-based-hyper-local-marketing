from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base
import datetime

class OTPAttempt(Base):
    __tablename__ = "otp_attempts"
    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, nullable=False)
    otp_code = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)