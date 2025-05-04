from pydantic import BaseModel

class SendOTPRequest(BaseModel):
    mobile_number: str

class VerifyOTPRequest(BaseModel):
    mobile_number: str
    otp_code: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"