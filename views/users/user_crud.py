from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User
from schemas.user_schemas import UserCreate,UserUpdate
from fastapi import Depends, HTTPException, status

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):

    return db.query(User).filter(User.username == username).first()

def get_user_by_useremail(db: Session, email: str):

    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    existing_user = db.query(User).filter(User.phone_number == user.phone_number).first()
    print(" recive",user.phone_number)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Phone number already exists. Please use a different number."
        )

    # Hash the password only if provided; otherwise, set to None
    hashed_password = pwd_context.hash(user.password) if user.password else None

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        phone_number=user.phone_number,
        city_name=user.city_name,
        country_name=user.country_name,
        address=user.address,
        googleId=user.googleId  # Include googleId if provided
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(db: Session, email: str, password: str):

    user = get_user_by_useremail(db, email)

    if user and pwd_context.verify(password, user.password_hash):

        return user
    
    return None

def get_user_by_email_or_googleId(db: Session, email: str, googleId: str):
    return db.query(User).filter((User.email == email) | (User.googleId == googleId)).first()


def update_user_details(
    db: Session,
    current_user: str,
    user_update: UserUpdate
):
    db_user = get_user_by_username(db, current_user)

    if not db_user:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user_update.phone_number:
        db_user.phone_number = user_update.phone_number

    if user_update.password:

        db_user.password_hash = pwd_context.hash(user_update.password)  

    db.add(db_user)

    db.commit()
    
    db.refresh(db_user)

    return db_user

def get_user_by_id(db: Session, user_id: int):

    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return db_user