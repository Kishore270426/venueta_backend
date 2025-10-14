from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import Admin  
from schemas.admin_schemas import AdminCreate, AdminUpdate
from fastapi import HTTPException, status

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_admin_by_username(db: Session, username: str):

    return db.query(Admin).filter(Admin.username == username).first()

def get_admin_by_email(db: Session, email: str):

    return db.query(Admin).filter(Admin.email == email).first()

def get_admin_by_email_and_googleId(db: Session, email: str, googleId: str):
    return db.query(Admin).filter((Admin.email == email) | (Admin.googleId == googleId)).first()

def create_admin(db: Session, admin: AdminCreate):
    existing_user = db.query(Admin).filter(Admin.phone_number == admin.phone_number).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already exists. Please use a different number.")

    # Ensure at least one of password or google_id is provided
    if not admin.password and not admin.googleId:
        raise HTTPException(status_code=400, detail="Either password or Google ID must be provided.")

    hashed_password = pwd_context.hash(admin.password) if admin.password else None

    db_admin = Admin(
        username=admin.username,
        email=admin.email,
        password_hash=hashed_password,
        googleId=admin.googleId,
        phone_number=admin.phone_number,
        address=admin.address,
        state=admin.state,
        country=admin.country,
    )

    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)

    return db_admin

def authenticate_admin(db: Session, username: str, password: str):

    admin = get_admin_by_username(db, username)

    if admin and pwd_context.verify(password, admin.password_hash):

        return admin
    
    return None
def authenticate_adminbyemail(db: Session, email: str, password: str):

    admin = get_admin_by_email(db, email)

    if admin and pwd_context.verify(password, admin.password_hash):

        return admin
    
    return None

def update_admin_details(
    db: Session,
    current_admin: str,
    admin_update: AdminUpdate
):
    db_admin = get_admin_by_username(db, current_admin)

    if not db_admin:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    # Update only the fields that are provided
    update_data = admin_update.dict(exclude_unset=True)

    for key, value in update_data.items():

        setattr(db_admin, key, value)

    db.add(db_admin)

    db.commit()
    
    db.refresh(db_admin)

    return db_admin
