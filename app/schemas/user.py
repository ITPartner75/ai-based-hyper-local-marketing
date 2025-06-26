from pydantic import BaseModel

class UserLogout(BaseModel):
    mobile_number: str

class UserLogin(BaseModel):
    mobile_number: str
    password: str

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    password: str
    mobile_number: str

class UserOut(BaseModel):
    id: int
    mobile_number: str
    role: str
    is_active: bool
    model_config = {
        "from_attributes": True  # ✅ Enables `.from_orm()` in Pydantic v2
    }