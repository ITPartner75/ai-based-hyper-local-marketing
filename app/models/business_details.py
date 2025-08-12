from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Float, JSON, LargeBinary
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# class Media(Base):
#     __tablename__ = "media"
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     business_id = Column(Integer, ForeignKey("business.id"), nullable=False)
#     images = Column(LargeBinary, nullable=True)     # ✅ binary image data
#     logo = Column(LargeBinary, nullable=True)
#     brouchure = Column(LargeBinary, nullable=True)
#     report = Column(LargeBinary, nullable=True)
#     videos = Column(LargeBinary, nullable=True)     # ✅ binary video data
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_id = Column(Integer, ForeignKey("business.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    files = relationship("MediaFile", back_populates="media", cascade="all, delete-orphan")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class MediaFile(Base):
    __tablename__ = "media_files"
    id = Column(Integer, primary_key=True)
    media_id = Column(Integer, ForeignKey("media.id", ondelete="CASCADE"))
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # image, video, brochure, etc.
    file_data = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    media = relationship("Media", back_populates="files")

class Contact(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_id = Column(Integer, ForeignKey("business.id"), nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(
        JSON,
        nullable=True,
        default=lambda: {
            "city": None,
            "state": None,
            "country": None,
            "postal_code": None,
            "coordinates": None
        }
    )
    # social_media = Column(String, nullable=True)
    social_media = Column(
        JSON,
        nullable=True,
        default=lambda: {
            "facebook": None,
            "instagram": None,
            "google_business": None
        }
    )
    website = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class BusinessDetails(Base):
    __tablename__ = "business_details"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_id = Column(Integer, ForeignKey("business.id"), nullable=False)
    media_id = Column(Integer, ForeignKey("media.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contact.id"), nullable=False)
    products = relationship("Product", back_populates="business_details", cascade="all, delete-orphan")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    business_details_id = Column(Integer, ForeignKey("business_details.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    image_name = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    image_data = Column(String, nullable=True)
    image_mime = Column(String, nullable=True)
    image_size = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    business_details = relationship("BusinessDetails", back_populates="products")