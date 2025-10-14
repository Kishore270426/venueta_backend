from fastapi import  Depends, HTTPException, status, UploadFile, File, Form,APIRouter
from sqlalchemy.orm import Session
from typing import List
from database_config.database import get_db
from models import Admin, EventHallRegister
import json
from services.auth import get_current_admin
import shutil
import os
from schemas.hall_schemas import HallResponse
from fastapi import Request
from models import EventHallRegister, Subscription, FreeTrial
from sqlalchemy.sql import and_, or_, text

hall_register_router = APIRouter()

@hall_register_router.post("/register")
async def register_hall(
    request: Request,
    hall_name: str = Form(...),
    hall_location: str = Form(...),
    hall_address: str = Form(...),
    hall_price_per_day: float = Form(...),
    maintenance_charge_per_day: float = Form(...),
    cleaning_charge_per_day: float = Form(...),
    catering_work_members: int = Form(...),
    total_hall_capacity: int = Form(...),
    number_of_rooms: int = Form(...),
    about_hall: str = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
    
):

    # Ensure the images directory exists
    upload_dir = "uploaded_images"
    os.makedirs(upload_dir, exist_ok=True)

    # Validate the number of images
    if len(images) < 3 or len(images) > 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload between 3 to 8 images."
        )

    # Process images and generate URLs
    image_urls = []
    # base_url = "http://127.0.0.1:8000"  # Replace with your actual server's base URL
    base_url = str(request.base_url).rstrip("/")
    for image in images:
        image_path = os.path.join(upload_dir, image.filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        # Create URL path for the image
        image_urls.append(f"{base_url}/uploaded_images/{image.filename}")

    # Register new hall in the database
    new_hall = EventHallRegister(
        hall_name=hall_name,
        hall_location=hall_location,
        hall_address=hall_address,
        hall_price_per_day=hall_price_per_day,
        maintenance_charge_per_day=maintenance_charge_per_day,
        cleaning_charge_per_day=cleaning_charge_per_day,
        catering_work_members=catering_work_members,
        total_hall_capacity=total_hall_capacity,
        number_of_rooms=number_of_rooms,
        about_hall=about_hall,
        image_url=json.dumps(image_urls),  
        admin_id=current_admin.id,
    )

    db.add(new_hall)
    db.commit()
    db.refresh(new_hall)

    # Parse the JSON string back to a list for the response
    image_urls = json.loads(new_hall.image_url)

    # Return the hall details along with image URLs
    return {
        "id": new_hall.id,
        "hall_name": new_hall.hall_name,
        "hall_location": new_hall.hall_location,
        "hall_address": new_hall.hall_address,
        "hall_price_per_day": new_hall.hall_price_per_day,
        "maintenance_charge_per_day": new_hall.maintenance_charge_per_day,
        "cleaning_charge_per_day": new_hall.cleaning_charge_per_day,
        "catering_work_members": new_hall.catering_work_members,
        "total_hall_capacity": new_hall.total_hall_capacity,
        "number_of_rooms": new_hall.number_of_rooms,
        "about_hall": new_hall.about_hall,
        "image_urls": image_urls,  # Return the list of image URLs
        "admin_id": new_hall.admin_id,
    }


@hall_register_router.get("/get_all_halls")
async def get_halls(db: Session = Depends(get_db)):
    # ✅ Fetch all halls without filtering by admin_id
    halls = db.query(EventHallRegister).all()

    # ✅ Prepare the list of hall details with image URLs
    hall_list = []
    for hall in halls:
        # Handle invalid or empty image URLs
        try:
            image_urls = json.loads(hall.image_url) if hall.image_url else []
        except json.JSONDecodeError:
            image_urls = []

        hall_list.append({
            "id": hall.id,
            "hall_name": hall.hall_name,
            "hall_location": hall.hall_location,
            "hall_address": hall.hall_address,
            "hall_price_per_day": hall.hall_price_per_day,
            "maintenance_charge_per_day": hall.maintenance_charge_per_day,
            "cleaning_charge_per_day": hall.cleaning_charge_per_day,
            "catering_work_members": hall.catering_work_members,
            "total_hall_capacity": hall.total_hall_capacity,
            "number_of_rooms": hall.number_of_rooms,
            "about_hall": hall.about_hall,
            "image_urls": image_urls,
            "admin_id": hall.admin_id,
        })

    return {"halls": hall_list}

@hall_register_router.get("/get_halls_for_admin_based/{admin_id}")
async def get_halls(admin_id: int, db: Session = Depends(get_db)):
    # ✅ Fetch halls for the given admin_id
    halls = db.query(EventHallRegister).filter(EventHallRegister.admin_id == admin_id).all()

    # ✅ Prepare the list of hall details with image URLs
    hall_list = []
    for hall in halls:
        # Handle invalid or empty image URLs
        try:
            image_urls = json.loads(hall.image_url) if hall.image_url else []
        except json.JSONDecodeError:
            image_urls = []

        hall_list.append({
            "id": hall.id,
            "hall_name": hall.hall_name,
            "hall_location": hall.hall_location,
            "hall_address": hall.hall_address,
            "hall_price_per_day": hall.hall_price_per_day,
            "maintenance_charge_per_day": hall.maintenance_charge_per_day,
            "cleaning_charge_per_day": hall.cleaning_charge_per_day,
            "catering_work_members": hall.catering_work_members,
            "total_hall_capacity": hall.total_hall_capacity,
            "number_of_rooms": hall.number_of_rooms,
            "about_hall": hall.about_hall,
            "image_urls": image_urls,
            "admin_id": hall.admin_id,
        })

    return {"halls": hall_list}



# for user
@hall_register_router.get("/get_halls")
async def get_halls(db: Session = Depends(get_db)):
    today = db.execute(text("SELECT current_date")).scalar()  # Get today's date from DB

    # ✅ Fetch halls where the admin has either an active subscription OR an active free trial
    subscribed_halls = (
        db.query(EventHallRegister)
        .join(Subscription, Subscription.admin_id == EventHallRegister.admin_id, isouter=True)
        .join(FreeTrial, FreeTrial.admin_id == EventHallRegister.admin_id, isouter=True)
        .filter(
            or_(
                Subscription.expiry_date >= today,  # Active subscription
                FreeTrial.expiry_date >= today      # Active free trial
            )
        )
        .all()
    )

    # ✅ Prepare the list of hall details with image URLs
    hall_list = []
    for hall in subscribed_halls:
        # Handle invalid or empty image URLs
        try:
            image_urls = json.loads(hall.image_url) if hall.image_url else []
        except json.JSONDecodeError:
            image_urls = []

        hall_list.append({
            "id": hall.id,
            "hall_name": hall.hall_name,
            "hall_location": hall.hall_location,
            "hall_address": hall.hall_address,
            "hall_price_per_day": hall.hall_price_per_day,
            "maintenance_charge_per_day": hall.maintenance_charge_per_day,
            "cleaning_charge_per_day": hall.cleaning_charge_per_day,
            "catering_work_members": hall.catering_work_members,
            "total_hall_capacity": hall.total_hall_capacity,
            "number_of_rooms": hall.number_of_rooms,
            "about_hall": hall.about_hall,
            "image_urls": image_urls,
            "admin_id": hall.admin_id,
        })

    # ✅ Return only halls where the admin has an active subscription or free trial
    return {"halls": hall_list}


@hall_register_router.put("/update/{hall_id}", response_model=HallResponse, status_code=status.HTTP_200_OK)
async def update_hall(

    hall_id: int,

    hall_name: str = Form(None),

    hall_location: str = Form(None),

    hall_address: str = Form(None),

    hall_price_per_day: float = Form(None),

    maintenance_charge_per_day: float = Form(None),

    cleaning_charge_per_day: float = Form(None),

    catering_work_members: int = Form(None),

    total_hall_capacity: int = Form(None),

    number_of_rooms: int = Form(None),

    about_hall: str = Form(None),

    image: UploadFile = File(None),

    db: Session = Depends(get_db),

    current_admin: Admin = Depends(get_current_admin)
):
   
    hall = db.query(EventHallRegister).filter(EventHallRegister.id == hall_id, EventHallRegister.admin_id == current_admin.id).first()

    if not hall:

        raise HTTPException(status_code=404, detail="Hall not found")

    
    if hall_name:
        hall.hall_name = hall_name

    if hall_location:
        hall.hall_location = hall_location

    if hall_address:
        hall.hall_address = hall_address

    if hall_price_per_day:
        hall.hall_price_per_day = hall_price_per_day

    if maintenance_charge_per_day:
        hall.maintenance_charge_per_day = maintenance_charge_per_day

    if cleaning_charge_per_day:
        hall.cleaning_charge_per_day = cleaning_charge_per_day

    if catering_work_members:
        hall.catering_work_members = catering_work_members

    if total_hall_capacity:
        hall.total_hall_capacity = total_hall_capacity

    if number_of_rooms:
        hall.number_of_rooms = number_of_rooms

    if about_hall:
        hall.about_hall = about_hall
    
   
    if image:

        upload_dir = "uploaded_images"

        os.makedirs(upload_dir, exist_ok=True)

        image_url = os.path.join(upload_dir, image.filename)

        with open(image_url, "wb") as buffer:

            shutil.copyfileobj(image.file, buffer)

        hall.image_url = image_url  

    
    db.commit()

    db.refresh(hall)

    return HallResponse(

        id=hall.id,

        hall_name=hall.hall_name,

        hall_location=hall.hall_location,

        hall_address=hall.hall_address,

        hall_price_per_day=hall.hall_price_per_day,

        maintenance_charge_per_day=hall.maintenance_charge_per_day,

        cleaning_charge_per_day=hall.cleaning_charge_per_day,

        catering_work_members=hall.catering_work_members,

        total_hall_capacity=hall.total_hall_capacity,

        number_of_rooms=hall.number_of_rooms,

        about_hall=hall.about_hall,

        image_path=hall.image_url
    )
