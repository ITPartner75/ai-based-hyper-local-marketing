from sqlalchemy import Column, Integer, String, Boolean, DateTime
from db.base import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    role = Column(String, default="Normal")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)