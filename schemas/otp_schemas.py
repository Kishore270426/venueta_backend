from pydantic import BaseModel


class MobileRequest(BaseModel):

    mobile: str


class OTPRequest(BaseModel):

    mobile: str
    
    otp: str
