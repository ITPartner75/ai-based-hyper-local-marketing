from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    mobile_number: str

class UserOut(BaseModel):
    id: int
    mobile_number: str
    role: str
    is_active: bool
    class Config:
        orm_mode = True