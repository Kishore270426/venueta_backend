from email.message import EmailMessage
import smtplib
from schemas.invoice import InvoiceResponse ,InvoiceCreate
from fastapi import APIRouter, Depends,HTTPException

def send_invoice(sender_email: str, sender_password: str, recipient_email: str, subject: str, body: str):
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