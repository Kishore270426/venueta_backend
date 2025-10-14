from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime

# Schema to accept admin login request (username + password)
class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = None
    googleId: Optional[str] = None

    @model_validator(mode="after")
    def check_credentials(cls, values):
        if not values.password and not values.googleId:
            raise ValueError("Either password or googleId must be provided.")
        return values
# Schema for the tokens (access token, refresh token)
class AdminToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_id:int
    admin_name:str

# Admin Base Schema (for admin-related data)
class AdminBase(BaseModel):
    username: str
    email: str
    phone_number: str
    address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

# Admin registration schema with password
class AdminCreate(AdminBase):
    password: str = None
    googleId: str = None

    


# Admin output schema (response model with id and created_at)
class AdminOut(AdminBase):
    id: int
    created_at: datetime

# Admin update schema
class   AdminUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    password: Optional[str] = None
