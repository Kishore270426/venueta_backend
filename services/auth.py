from datetime import datetime, timedelta
from typing import Union
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from views.users import user_crud
from services import auth as utils
from database_config.database import get_db
from dotenv import load_dotenv
import os

from views.admin import admin_crud_views as admin_crud

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))

REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):

    if expires_delta:

        expire = datetime.utcnow() + expires_delta

    else:

        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode = data.copy()

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict):

    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = data.copy()

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload
    
    except JWTError:

        return None
    

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    payload = utils.verify_token(token)

    if payload is None:

        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    username = payload.get("sub")

    if username is None:

        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = user_crud.get_user_by_username(db, username)
    
    if user is None:

        raise HTTPException(status_code=404, detail="User not found")
    
    return user.username

def get_current_userID(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    payload = utils.verify_token(token)

    if payload is None:

        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    username = payload.get("sub")

    if username is None:

        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = user_crud.get_user_by_username(db, username)
    
    if user is None:

        raise HTTPException(status_code=404, detail="User not found")
    
    return user


def get_current_admin(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    payload = utils.verify_token(token)

    if payload is None:

        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    adminname = payload.get("sub")

    if adminname is None:

        raise HTTPException(status_code=401, detail="Invalid token")
    
    admin = admin_crud.get_admin_by_username(db, adminname)
    
    if admin is None:

        raise HTTPException(status_code=404, detail="User not found")
    
    return admin

def get_current_adminbyID(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    payload = utils.verify_token(token)

    if payload is None:

        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    adminname = payload.get("sub")

    if adminname is None:

        raise HTTPException(status_code=401, detail="Invalid token")
    
    admin = admin_crud.get_admin_by_username(db, adminname)
    
    if admin is None:

        raise HTTPException(status_code=404, detail="User not found")
    
    return admin.id




