from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BusinessBase(BaseModel):
    business_name: str
    business_category: str

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BusinessBase):
    is_active: Optional[bool] = True

class BusinessOut(BusinessBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
