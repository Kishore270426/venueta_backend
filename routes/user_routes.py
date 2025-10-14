from fastapi import Depends,APIRouter 
from sqlalchemy.orm import Session
from schemas import user_schemas
from views.users import user_crud
from database_config.database import get_db
from schemas import user_schemas as schemas
from services import auth
from services import auth as utils 
from views.users.user_views import delete_user_service ,refresh_token_service ,login_service ,register_user_service
from models import User

user_router= APIRouter()

@user_router.post("/register", response_model=user_schemas.UserOut)
def register(

    user: user_schemas.UserCreate,

    db: Session = Depends(get_db)
    
):
    return register_user_service(user, db)


@user_router.post("/login", response_model=user_schemas.UserToken)
def login(

    login_request: user_schemas.LoginRequest,

    db: Session = Depends(get_db)
):
    return login_service(login_request, db)


@user_router.post("/refresh", response_model=user_schemas.UserToken)
def refresh_token(

    refresh_token: str,

    db: Session = Depends(get_db)
):
    return refresh_token_service(refresh_token, db)


@user_router.patch("/update_user", response_model=schemas.UserOut)
def update_user(

    user_update: schemas.UserUpdate,

    db: Session = Depends(get_db),

    current_user: str = Depends(utils.get_current_user)
):
    return user_crud.update_user_details(db, current_user, user_update)


# @user_router.post("/update_password",response_model=schemas.UserOut)


@user_router.delete("/delete_user", response_model=None)
def delete_user(

    user_id: int,

    db: Session = Depends(get_db),

    current_user: str = Depends(auth.get_current_user)
):
    return delete_user_service(user_id, db)
