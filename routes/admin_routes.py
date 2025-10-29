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

from models.event_hall_register import EventHallRegister


sender_email="riverpearlsolutions@gmail.com"
sender_password="erny ltum bxfy vtuz"

@admin_router.post("/invoices/", response_model=InvoiceResponse)
async def create_invoice(
    invoice_data: InvoiceCreate, 
    db: Session = Depends(get_db), 
    current_admin: str = Depends(auth.get_current_adminbyID)
):
    
    try:
        hall_name_id=invoice_data.hall_id
        hall = db.query(EventHallRegister).filter(EventHallRegister.id == hall_name_id).first()
        if not hall:
            raise HTTPException(status_code=404, detail="Hall not found")
        hall_name = hall.hall_name
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
                hall_name=hall_name,
                adminname=admin.username,
                adminphonenumber=admin.phone_number, 
                admin_email=admin.email,
                adminaddress=admin.address,
                admincity=admin.state,
                admincountry=admin.country,
                
                useremail=invoice_data.useremail,
                
                maintenance_charge=invoice_data.maintenance_charge,
                cleaning_charge=invoice_data.cleaning_charge,
                total_price=invoice_data.hall_total_price,
                sender_email=sender_email,
                sender_password=sender_password
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error sending invoice email: {str(e)}")

        return new_invoice
    except Exception as e:
        # If any other unexpected error occurs
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")



from datetime import datetime
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from email.message import EmailMessage
import smtplib
import os
from fastapi import HTTPException

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
    hall_name: str,
    sender_email: str,
    sender_password: str,
):
    # Generate invoice ID
    invoice_id = f"INV-{random.randint(10000, 99999)}"
    current_date = datetime.now().strftime("%B %d, %Y")

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
    width, height = letter

    # Modern gradient header - Purple to Blue
    c.setFillColorRGB(0.29, 0.24, 0.55)  # Deep purple
    c.rect(0, height - 130, width, 130, fill=1, stroke=0)
    
    # Accent stripe
    c.setFillColorRGB(0.95, 0.61, 0.07)  # Gold/Orange accent
    c.rect(0, height - 140, width, 10, fill=1, stroke=0)

    # INVOICE ID and DATE - Left side (as requested)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0.95, 0.61, 0.07)
    c.drawString(50, height - 50, "INVOICE NO:")
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(50, height - 70, invoice_id)
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0.95, 0.61, 0.07)
    c.drawString(50, height - 90, "DATE:")
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(50, height - 110, current_date)

    # INVOICE text - Right side of header
    c.setFont("Helvetica-Bold", 42)
    c.setFillColorRGB(1, 1, 1)
    c.drawRightString(width - 50, height - 80, "INVOICE")

    # Company Info - Right side
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(1, 1, 1)
    c.drawRightString(width - 50, height - 110, f"{adminname}")
    
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.drawRightString(width - 50, height - 125, f"Phone: {adminphonenumber} | Email: {admin_email}")

    # Hall Name - Centered heading below header
    c.setFillColorRGB(0.95, 0.95, 0.97)  # Light gray background
    c.rect(50, height - 200, width - 100, 40, fill=1, stroke=0)
    
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0.29, 0.24, 0.55)
    hall_text_width = c.stringWidth(hall_name.upper(), "Helvetica-Bold", 20)
    c.drawString((width - hall_text_width) / 2, height - 185, hall_name.upper())

    # Left border accent
    c.setFillColorRGB(0.95, 0.61, 0.07)
    c.rect(50, height - 200, 5, 40, fill=1, stroke=0)

    # FROM and TO Address Sections - Side by side
    y_start = height - 260
    
    # FROM Section - Left side
    c.setFillColorRGB(0.98, 0.98, 0.99)
    c.roundRect(50, y_start - 120, 250, 110, 5, fill=1, stroke=0)
    
    # Header bar
    c.setFillColorRGB(0.29, 0.24, 0.55)
    c.roundRect(50, y_start - 20, 250, 25, 5, fill=1, stroke=0)
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(60, y_start - 15, "FROM")

    # Admin details
    c.setFont("Helvetica-Bold", 11)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.drawString(60, y_start - 45, adminname)
    
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(60, y_start - 60, f"📱 {adminphonenumber}")
    c.drawString(60, y_start - 75, f"📧 {admin_email}")
    c.drawString(60, y_start - 90, f"📍 {adminaddress}")
    c.drawString(60, y_start - 105, f"   {admincity}, {admincountry}")

    # TO Section - Right side
    c.setFillColorRGB(0.98, 0.98, 0.99)
    c.roundRect(320, y_start - 120, 230, 110, 5, fill=1, stroke=0)
    
    # Header bar
    c.setFillColorRGB(0.95, 0.61, 0.07)
    c.roundRect(320, y_start - 20, 230, 25, 5, fill=1, stroke=0)
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(330, y_start - 15, "BILL TO")

    # Customer details
    c.setFont("Helvetica-Bold", 11)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.drawString(330, y_start - 45, username)
    
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(330, y_start - 60, f"📱 {userphonenumber}")
    c.drawString(330, y_start - 75, f"📧 {useremail}")
    c.drawString(330, y_start - 90, f"📍 {useraddress}")
    c.drawString(330, y_start - 105, f"   {usercity}, {usercountry}")

    # Billing Calculation Table - As requested
    table_y = y_start - 160
    
    # Calculate amounts as per requirements
    final_price = maintenance_charge + cleaning_charge + total_price
    gst_amount = final_price * 0.18
    grand_total = final_price + gst_amount

    # Table data with proper calculations
    data = [
        ['#', 'DESCRIPTION', 'AMOUNT (₹)'],
        ['1', 'Maintenance Charge', f'{maintenance_charge:,.2f}'],
        ['2', 'Cleaning Charge', f'{cleaning_charge:,.2f}'],
        ['3', 'Total Price', f'{total_price:,.2f}'],
        ['', 'Final Price (1+2+3)', f'{final_price:,.2f}'],
        ['', 'GST (18%)', f'{gst_amount:,.2f}'],
        ['', 'GRAND TOTAL', f'{grand_total:,.2f}'],
    ]

    table = Table(data, colWidths=[40, 360, 100], rowHeights=[32, 25, 25, 25, 25, 25, 30])
    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A3F70')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        
        # Data rows (1-3)
        ('BACKGROUND', (0, 1), (-1, 3), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, 3), colors.black),
        ('FONTNAME', (0, 1), (0, 3), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (-1, 3), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, 3), 10),
        ('ALIGN', (0, 1), (0, 3), 'CENTER'),
        ('ALIGN', (1, 1), (1, 3), 'LEFT'),
        ('ALIGN', (2, 1), (2, 3), 'RIGHT'),
        
        # Final Price row
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#F5F5F5')),
        ('TEXTCOLOR', (0, 4), (-1, 4), colors.black),
        ('FONTNAME', (1, 4), (-1, 4), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 4), (-1, 4), 10),
        ('ALIGN', (1, 4), (1, 4), 'RIGHT'),
        ('ALIGN', (2, 4), (2, 4), 'RIGHT'),
        
        # GST row
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#F0F0F0')),
        ('TEXTCOLOR', (0, 5), (-1, 5), colors.black),
        ('FONTNAME', (1, 5), (-1, 5), 'Helvetica'),
        ('FONTSIZE', (0, 5), (-1, 5), 10),
        ('ALIGN', (1, 5), (1, 5), 'RIGHT'),
        ('ALIGN', (2, 5), (2, 5), 'RIGHT'),
        
        # Grand Total row - Highlighted
        ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#4A3F70')),
        ('TEXTCOLOR', (0, 6), (-1, 6), colors.white),
        ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 6), (-1, 6), 12),
        ('ALIGN', (1, 6), (1, 6), 'RIGHT'),
        ('ALIGN', (2, 6), (2, 6), 'RIGHT'),
        
        # Grid and styling
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#4A3F70')),
        ('LINEABOVE', (0, 4), (-1, 4), 1, colors.HexColor('#4A3F70')),
        ('LINEABOVE', (0, 6), (-1, 6), 2, colors.HexColor('#4A3F70')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    table.wrapOn(c, 50, 50)
    table.drawOn(c, 50, table_y)

    # Payment Instructions
    payment_y = table_y - 80
    c.setFillColorRGB(0.98, 0.98, 0.99)
    c.roundRect(50, payment_y - 60, width - 100, 50, 5, fill=1, stroke=0)
    
    c.setFillColorRGB(0.95, 0.61, 0.07)
    c.roundRect(50, payment_y - 10, width - 100, 25, 5, fill=1, stroke=0)
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(60, payment_y - 5, "PAYMENT INSTRUCTIONS")
    
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(60, payment_y - 30, "Payment Method: Online Transfer / Cash")
    c.drawString(60, payment_y - 45, f"Due Date: {current_date}")

    # Terms & Conditions
    terms_y = payment_y - 80
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0.29, 0.24, 0.55)
    c.drawString(50, terms_y, "TERMS & CONDITIONS")
    
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(50, terms_y - 15, "• Payment is due within 7 days of invoice date")
    c.drawString(50, terms_y - 28, "• Late payments may incur additional charges")
    c.drawString(50, terms_y - 41, "• Please bring a copy of this invoice on the day of booking")

    # Footer
    c.setStrokeColorRGB(0.95, 0.61, 0.07)
    c.setLineWidth(3)
    c.line(50, 70, width - 50, 70)
    
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(0.29, 0.24, 0.55)
    c.drawCentredString(width / 2, 50, "Thank you for your business!")
    
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width / 2, 35, f"For inquiries: {admin_email} | Phone: {adminphonenumber}")
    c.drawCentredString(width / 2, 23, "This is a computer-generated invoice")

    c.save()

    try:
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = useremail
        msg["Subject"] = f"Invoice {invoice_id} - {hall_name} Booking"
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