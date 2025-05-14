from sqlalchemy import Column, Integer, String, DateTime
from db.base import Base
import datetime

class AccessHistory(Base):
    __tablename__ = "access_history"
    id = Column(Integer, primary_key=True, index=True)
    # username = Column(String, nullable=False)
    mobile_number = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)
    access_status = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)