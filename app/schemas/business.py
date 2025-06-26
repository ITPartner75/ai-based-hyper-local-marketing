from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi import UploadFile, File

class BusinessBase(BaseModel):
    business_name: str
    business_category: str

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BaseModel):
    business_name: Optional[str] = None
    business_category: Optional[str] = None
    is_active: Optional[bool] = True

class BusinessOut(BusinessBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True  # ✅ Enables `.from_orm()` in Pydantic v2
    }

#Media
class MediaBase(BaseModel):
    images: Optional[bytes] = None
    logo: Optional[bytes] = None
    brouchure: Optional[bytes] = None
    report: Optional[bytes] = None
    videos: Optional[bytes] = None

    model_config = {
        "from_attributes": True  # ✅ Enables `.from_orm()` in Pydantic v2
    }

class MediaCreate(MediaBase): pass

class MediaUpdate(MediaBase): 
    is_active: Optional[bool] = True

class MediaOut(MediaBase):
    id: int
    user_id: int
    business_id: int
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True  # ✅ Enables `.from_orm()` in Pydantic v2
    }

#Contact
class ContactBase(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    social_media: Optional[str] = None
    website: Optional[str] = None

    model_config = {
        "from_attributes": True  # ✅ Enables `.from_orm()` in Pydantic v2
    }

class ContactCreate(ContactBase): pass

class ContactUpdate(ContactBase):
    is_active: Optional[bool] = True

class ContactOut(ContactBase):
    id: int
    user_id: int
    business_id: int
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True  # ✅ Enables `.from_orm()` in Pydantic v2
    }

#Business Details
class BusinessDetailsBase(BaseModel):
    products: Optional[list[str]] = None

class BusinessDetailsCreate(BusinessDetailsBase): pass

class BusinessDetailsUpdate(BusinessDetailsBase):
    is_active: Optional[bool] = True

class BusinessDetailsOut(BusinessDetailsBase):
    media: Optional[MediaBase] = None
    contact: Optional[ContactBase] = None

    model_config = {
        "from_attributes": True  # ✅ Enables `.from_orm()` in Pydantic v2
    }