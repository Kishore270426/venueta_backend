from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional


class MessageResponse(BaseModel):

    message: str


class UserBase(BaseModel):

    username: str

    email: str

class UserCreate(UserBase):
    password: Optional[str] = None  # Made optional to support Google registration
    
    phone_number: Optional[str] = None
    
    city_name: Optional[str] = None
    
    country_name: Optional[str] = None
    
    address: Optional[str] = None
    
    googleId: Optional[str] = None  # New field for storing Google ID



class UserToken(BaseModel):

    user_id: int 

    user_name: str
    
    user_email:str

    user_access_token: str

    user_refresh_token: str

    token_type: str
    


class UserOut(UserBase):

    id: int

    created_at: datetime

    phone_number: Optional[str] = None

    city_name: Optional[str] = None

    country_name: Optional[str] = None

    address: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = None
    googleId: Optional[str] = None

    @model_validator(mode="after")
    def check_credentials(cls, values):
        if not values.password and not values.googleId:
            raise ValueError("Either password or googleId must be provided.")
        return values

class UserUpdate(BaseModel):

    password: Optional[str] = None

    phone_number: Optional[str] = None
