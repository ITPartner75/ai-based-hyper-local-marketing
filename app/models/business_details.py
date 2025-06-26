from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base import Base
from typing import List
import datetime

class Business(Base):
    __tablename__ = "business"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_name = Column(String, nullable=False)
    business_category = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_id = Column(Integer, ForeignKey("business.id"), nullable=False)
    images = Column(LargeBinary, nullable=True)     # ✅ binary image data
    logo = Column(LargeBinary, nullable=True)
    brouchure = Column(LargeBinary, nullable=True)
    report = Column(LargeBinary, nullable=True)
    videos = Column(LargeBinary, nullable=True)     # ✅ binary video data
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class Contact(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_id = Column(Integer, ForeignKey("business.id"), nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    social_media = Column(String, nullable=True)
    website = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class BusinessDetails(Base):
    __tablename__ = "business_details"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_id = Column(Integer, ForeignKey("business.id"), nullable=False)
    media_id = Column(Integer, ForeignKey("media.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contact.id"), nullable=False)
    products = Column(ARRAY(String), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
