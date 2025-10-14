from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from services import auth
from . import  user_crud


def register_user_service(user, db: Session):

    # db_user = user_crud.get_user_by_username(db, user.username)
    db_user = user_crud.get_user_by_useremail(db, user.email)

    if db_user:
        raise HTTPException(status_code=400, detail="Useremail already registered")
    
    # Create the new user
    return user_crud.create_user(db, user)

def login_service(login_request, db: Session):
    # If googleId is provided, try to get the user by googleId
    if login_request.googleId:
        user = user_crud.get_user_by_email_or_googleId(db,login_request.email, login_request.googleId)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid Google credentials")
    else:
        # Otherwise, authenticate using email and password
        user = user_crud.authenticate_user(db, login_request.email, login_request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    refresh_token = auth.create_refresh_token(data={"sub": user.username})
    
    return {
        "user_id": user.id,
        "user_email":user.email,
        "user_name": user.username,
        "user_access_token": access_token,
        "user_refresh_token": refresh_token,
        "token_type": "bearer"
    }



def delete_user_service(user_id: int, db: Session):

    user = user_crud.get_user_by_id(db, user_id)

    if not user:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="User not found"
        )   
    
    db.delete(user)

    db.commit()
    
    return {"message": "User successfully deleted"}



def refresh_token_service(refresh_token: str, db: Session):
    
    payload = auth.verify_token(refresh_token)

    if not payload:

        raise HTTPException(status_code=403, detail="Invalid or expired refresh token")
    
    username = payload.get("sub")

    user = user_crud.get_user_by_username(db, username)
    
    if not user:

        raise HTTPException(status_code=404, detail="User not found")
    

    access_token = auth.create_access_token(data={"sub": user.username})

    refresh_token = auth.create_refresh_token(data={"sub": user.username})
    
    return {
        "user_id": user.id,
        "user_name": user.username,
        "user_access_token": access_token,
        "user_refresh_token": refresh_token,
        "token_type": "bearer"
    }

