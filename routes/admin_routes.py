from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from schemas.admin_schemas import (
    LoginRequest, 
    AdminToken, 
    AdminOut, 
    AdminCreate, 
    AdminUpdate
)
from schemas.hall_schemas import BookingResponse,UpdateStatusRequest,Bookingapprovedlist
from services import auth
from views.admin import admin_crud_views as admin_crud
from database_config.database import get_db
from views.admin.admin_views import (
    register_admin_service, 
    login_admin_service, 
    refresh_admin_token_service,
    register_admin_servic_mobile
    
)
from models.booking import Booking
from models.admin import Admin
from models.user import User
from models.invoice_table import Invoice
from typing import List
from aiosmtplib import SMTP
from dotenv import load_dotenv
import os
from email.message import EmailMessage
from schemas.invoice import InvoiceResponse ,InvoiceCreate
import smtplib
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


admin_router = APIRouter()

load_dotenv()

recipient_email="letsmail.sakthivel@gmail.com"

sender_email = os.getenv('sender_email')
sender_password = os.getenv('sender_password')


@admin_router.post("/register", response_model=AdminOut)
def register_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db)
):
    """
    Handles admin registration.
    :param admin: Data for creating a new admin.
    :param db: Database session.
    :return: Details of the registered admin.
    """
    return register_admin_service(admin, db)

@admin_router.post("/register-Mobile", response_model=AdminOut)
def register_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db)
):
    """
    Handles admin registration.
    :param admin: Data for creating a new admin.
    :param db: Database session.
    :return: Details of the registered admin.
    """
    return register_admin_servic_mobile(admin, db)

@admin_router.post("/login", response_model=AdminToken)
def login_admin(
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Handles admin login and token generation.
    :param login_request: Login credentials.
    :param db: Database session.
    :return: Authentication tokens for the admin.
    """
    return login_admin_service(login_request, db)



@admin_router.post("/refresh", response_model=AdminToken)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refreshes the authentication token for an admin.
    :param refresh_token: Token to be refreshed.
    :param db: Database session.
    :return: New authentication tokens.
    """
    return refresh_admin_token_service(refresh_token, db)


# Endpoint for updating admin details
@admin_router.patch("/update", response_model=AdminOut)
def update_admin(
    admin_update: AdminUpdate, 
    db: Session = Depends(get_db), 
    current_admin: str = Depends(auth.get_current_admin)  
):
    
    return admin_crud.update_admin_details(db, current_admin, admin_update)



@admin_router.get("/bookings", response_model=List[BookingResponse])

def get_bookings_by_admin_id( current_admin: str = Depends(auth.get_current_adminbyID) , db: Session = Depends(get_db)):
    
    bookings = db.query(Booking).filter(Booking.admin_id == current_admin).all()
    
    if not bookings:
        
        raise HTTPException(status_code=200, detail="No bookings found for you")
    
    return bookings


@admin_router.get("/confirmstatus", response_model=List[BookingResponse])

def get_bookings_by_admin_id( current_admin: str = Depends(auth.get_current_adminbyID) , db: Session = Depends(get_db)):
    
    bookings = db.query(Booking).filter(Booking.admin_id == current_admin).all()
    
    if not bookings:
        
        raise HTTPException(status_code=404, detail="No bookings found for the given admin ID")
    
    return bookings


def send_email(sender_email: str, sender_password: str, recipient_email: str, subject: str, body: str):
    try:

        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.set_content(body)

       
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  
            server.login(sender_email, sender_password)  
            server.send_message(msg)  

        return {"message": "Email sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@admin_router.put("/bookings/updatestatus")
async def update_booking_status(
    request: UpdateStatusRequest,
    db: Session = Depends(get_db),
    current_admin: str = Depends(auth.get_current_adminbyID),
):
    
    booking = db.query(Booking).filter(Booking.id == request.id, Booking.admin_id == current_admin).first()
    
    # print(booking.user_email)
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = request.status
    db.commit()
    db.refresh(booking) 
    
    subject="Hall Registration Status"
    
    status = booking.status
    if status == "Pending":
         body="Your status is currently pending."
    elif status == "Approved":
         body="Hi, your hall has been successfully approved!"
    else:  
         body="Sorry, your hall has been rejected due to certain reasons."

    
    # send_email(sender_email, sender_password, booking.user_email, subject, body)
     
    return {"message": "Status updated successfully", "booking_id": booking.id, "status": booking.status}



@admin_router.get("/bookings/approved/", response_model=List[Bookingapprovedlist])
def get_approved_bookings_by_admin( db: Session = Depends(get_db),current_admin: str = Depends(auth.get_current_adminbyID)):

    approved_bookings = db.query(Booking).filter(Booking.admin_id == current_admin, Booking.status == "Approved",Booking.invoice_sent=="false").all()
    
    if not approved_bookings:
        raise HTTPException(status_code=404, detail="No approved bookings found for the given admin ID")
    
    return approved_bookings



# @admin_router.post("/invoices/", response_model=InvoiceResponse)
# def create_invoice(invoice_data: InvoiceCreate, db: Session = Depends(get_db), current_admin: str = Depends(auth.get_current_adminbyID)):

    
    
#     new_invoice = Invoice(
#         booking_id=invoice_data.booking_id,
#         hall_id=invoice_data.hall_id,
#         user_id=invoice_data.user_id,
#         maintenance_charge=invoice_data.maintenance_charge,
#         cleaning_charge=invoice_data.cleaning_charge,
#         hall_total_price=invoice_data.hall_total_price,
#     )
    
#     db.add(new_invoice)
#     db.commit()
#     db.refresh(new_invoice)
    
#     booking = db.query(Booking).filter(Booking.id == invoice_data.booking_id).first()
#     if booking:
#         booking.invoice_sent = True
#         db.commit()
#         db.refresh(booking)
#     else:
#         raise HTTPException(status_code=404, detail="Booking not found")
    
#     send_invoice(adminid ,recipient_email,invoice_data.user_id,invoice_data.cleaning_charge,invoice_data.maintenance_charge,invoice_data.hall_total_price)
    
#     return new_invoice


# def send_invoice(adminid ,recipient_email,invoice_data.user_id,invoice_data.cleaning_charge,invoice_data.maintenance_charge,invoice_data.hall_total_price):
    
#     admin = db.query(Admin).filter(Admin.id == adminid).first()
    
#     if not admin:
#         raise HTTPException(status_code=404, detail="Admin not found")
    
#     admindetails = Invoice(
       
#     )
#     try:

#         msg = EmailMessage()
#         msg["From"] = sender_email
#         msg["To"] = recipient_email
#         msg["Subject"] = "hall invoice bill"
#         msg.set_content(body)

       
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()  
#             server.login(sender_email, sender_password)  
#             server.send_message(msg)  

#         return {"message": "Email sent successfully"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@admin_router.post("/invoices/", response_model=InvoiceResponse)
async def create_invoice(
    invoice_data: InvoiceCreate, 
    db: Session = Depends(get_db), 
    current_admin: str = Depends(auth.get_current_adminbyID)
):
    
    try:
        
        try:
            new_invoice = Invoice(
                booking_id=invoice_data.booking_id,
                hall_id=invoice_data.hall_id,
                user_id=invoice_data.user_id,
                maintenance_charge=invoice_data.maintenance_charge,
                cleaning_charge=invoice_data.cleaning_charge,
                hall_total_price=invoice_data.hall_total_price,
                
            )
            db.add(new_invoice)
            db.commit() 
            db.refresh(new_invoice)  
            
        except Exception as e:
            db.rollback()  
            raise HTTPException(status_code=500, detail=f" db :1 :Error creating invoice: {str(e)}")

       
        try:
            booking = db.query(Booking).filter(Booking.id == invoice_data.booking_id).first()  # Async query
            print("Sucess")
            if booking:
                booking.invoice_sent = True
                db.commit()  # Await commit for async DB operations
                db.refresh(booking)  # Await refresh for async DB operations
            else:
                raise HTTPException(status_code=404, detail="Booking not found")
        except Exception as e:
            await db.rollback()  # Rollback if there's an error updating the booking
            raise HTTPException(status_code=500, detail=f"Error updating booking: {str(e)}")

        # Step 3: Fetch admin details
        try:
            admin =  db.query(Admin).filter(Admin.id == current_admin).first()  # Async query
            if not admin:
                raise HTTPException(status_code=404, detail="Admin not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"fetching admin det : Error fetching admin details: {str(e)}")

        # Step 4: Fetch user details
        try:
            user = db.query(User).filter(User.id == invoice_data.user_id).first()  # Async query
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"fetching user  det : Error fetching user details: {str(e)}")

        # Step 5: Send invoice email
        try:
            await send_invoice(  # Await the async email sending function
                username=user.username,
                userphonenumber=user.phone_number,
                useraddress=user.address,
                usercity=user.city_name,
                usercountry=user.country_name,
                
                adminname=admin.username,
                adminphonenumber=admin.phone_number, 
                admin_email=admin.email,
                adminaddress=admin.address,
                admincity=admin.state,
                admincountry=admin.country,
                
                useremail=invoice_data.useremail,
                
                maintenance_charge=invoice_data.maintenance_charge,
                cleaning_charge=invoice_data.cleaning_charge,
                total_price=invoice_data.hall_total_price
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error sending invoice email: {str(e)}")

        return new_invoice
    except Exception as e:
        # If any other unexpected error occurs
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")




async def send_invoice(
    username: str,
    userphonenumber: str,
    useraddress: str,
    usercity: str,
    usercountry: str,
    adminname: str,
    adminphonenumber: str,
    admin_email: str,
    adminaddress: str,
    admincity: str,
    admincountry: str,
    useremail: str,
    maintenance_charge: float,
    cleaning_charge: float,
    total_price: float,

):
    print(admin_email, admincity, admincountry)

    body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invoice Sent</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f7fa; padding: 20px;">
        <div class="container" style="background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
            <h2 class="text-center text-primary">Invoice Sent</h2>
            <p>Dear <strong>{username}</strong>,</p>
            <p>
                We are pleased to inform you that your hall booking invoice has been successfully processed. You can find the attached invoice PDF for your reference. Kindly take a moment to review it at your earliest convenience.
            </p>
            <p>
                Should you have any questions or concerns regarding the invoice or require further assistance, please do not hesitate to reach out. We are here to help and ensure you have a smooth experience.
            </p>
            <p>
                Thank you for choosing our services. We truly appreciate your trust in us and look forward to serving you again.
            </p>
            <p class="text-right" style="color: #888888;">
                Best regards,<br>
                <strong>{adminname}</strong><br>
                Admin Team
            </p>
            <hr>
            <p class="text-center" style="font-size: 12px; color: #aaa;">
                This is an automated message. If you have any questions, please reply to this email.
            </p>
        </div>
    </body>
    </html>
    """

    pdf_filename = "invoice.pdf"
    
    c = canvas.Canvas(pdf_filename, pagesize=letter)

   
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.black)  
    c.drawString(230, 770, "INVOICE")

   
    c.setLineWidth(2)
    c.setStrokeColor(colors.black)
    c.line(50, 760, 550, 760)

    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 720, "From")

    c.setFont("Helvetica", 10)
    c.drawString(50, 700, f"Name: {adminname}")
    c.drawString(50, 680, f"Phone Number: {adminphonenumber}")
    c.drawString(50, 660, f"Address: {adminaddress}, {admincity}, {admincountry}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, 720, "To")

    c.setFont("Helvetica", 10)
    c.drawString(300, 700, f"Name: {username}")
    c.drawString(300, 680, f"Phone Number: {userphonenumber}")
    c.drawString(300, 660, f"Address: {useraddress}, {usercity}, {usercountry}")

  
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(50, 640, 550, 640)

  
    data = [
        ['Description', 'Amount'],
        ['Maintenance Charge', f'{maintenance_charge}'],
        ['Cleaning Charge', f'{cleaning_charge}'],
        ['GST', "18%"],
        ['Total Price', f'{total_price}'],
    ]

    # Table
    table = Table(data, colWidths=[400, 100], rowHeights=[30] * len(data))
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),  
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  
        ('GRID', (0, 0), (-1, -1), 1, colors.black), 
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), 
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), 
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  
    ]))

  
    table.wrapOn(c, 50, 50)
    table.drawOn(c, 50, 400) 

   
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(50, 100, "Thank you for your business!")
    c.drawString(50, 85, "For any inquiries, contact us at support@admin.com")
    c.drawString(50, 70, "This invoice is generated automatically and is valid without a signature.")

   
    c.save()

    try:
        
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = useremail
        msg["Subject"] = "Hall Invoice Bill"
        msg.set_content(body, subtype="html")

       
        with open(pdf_filename, 'rb') as pdf_file:
            msg.add_attachment(pdf_file.read(), maintype='application', subtype='pdf', filename=pdf_filename)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  
            server.login(sender_email, sender_password)
            server.send_message(msg)

        
        os.remove(pdf_filename)

        return {"message": "Email sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

