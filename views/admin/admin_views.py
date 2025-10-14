from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from . import admin_crud_views as admin_crud
from services import auth


def register_admin_service(admin, db: Session):
    
    db_admin = admin_crud.get_admin_by_email(db, admin.email)

    if db_admin:

        raise HTTPException(status_code=400, detail="Admin Email already registered")
    
    return admin_crud.create_admin(db, admin)

def register_admin_servic_mobile(admin, db: Session):
    
    db_admin = admin_crud.get_admin_by_email(db, admin.email)

    if db_admin:

        raise HTTPException(status_code=400, detail="Admin Email already registered")
    
    return admin_crud.create_admin(db, admin)

def login_admin_service(login_request, db: Session):
    
    if login_request.googleId:
        admin = admin_crud.get_admin_by_email_and_googleId(db,login_request.email, login_request.googleId)
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid Google credentials")
    
    else:
   
        admin = admin_crud.authenticate_adminbyemail(db, login_request.email, login_request.password)
    
        if not admin:

            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    
    access_token = auth.create_access_token(data={"sub": admin.username})

    refresh_token = auth.create_refresh_token(data={"sub": admin.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id":admin.id,
        "admin_name":admin.username

    }

def refresh_admin_token_service(refresh_token: str, db: Session):
   
    payload = auth.verify_token(refresh_token)

    if not payload:

        raise HTTPException(status_code=403, detail="Invalid or expired refresh token")
    
    
    username = payload.get("sub")
    
   
    admin = admin_crud.get_admin_by_username(db, username)

    if not admin:

        raise HTTPException(status_code=404, detail="Admin not found")
    
    
    access_token = auth.create_access_token(data={"sub": admin.username})
    
    refresh_token = auth.create_refresh_token(data={"sub": admin.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id":admin.id
    }
