import random
import os
import time
import logging
from twilio.rest import Client
from dotenv import load_dotenv
from threading import Lock

load_dotenv()

logging.basicConfig(level=logging.INFO)

class OTPService:
    def __init__(self):
        self.TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
        self.TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN, self.TWILIO_PHONE_NUMBER]):
            raise ValueError("Missing required Twilio environment variables.")
        
        self.otp_storage = {}  # In-memory storage for OTPs
        self.lock = Lock()  # Thread-safe lock for OTP storage
        self.twilio_client = Client(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)

    def generate_otp(self) -> str:
        """Generate a 6-digit random OTP."""
        return str(random.randint(100000, 999999))

    def send_otp(self, mobile: str, otp: str):
        """Send OTP to the given mobile number using Twilio."""
        try:
            self.twilio_client.messages.create(
                body=f"Your OTP code is: {otp}",
                from_=self.TWILIO_PHONE_NUMBER,
                to=mobile
            )
            print("otp:",otp)
            logging.info(f"OTP sent successfully to {mobile}")
        except Exception as e:
            logging.error(f"Error sending OTP to {mobile}: {e}")
            raise RuntimeError("Failed to send OTP. Please try again later.")

    def store_otp(self, mobile: str, otp: str):
        """Store OTP and its timestamp in memory (thread-safe)."""
        with self.lock:
            self.otp_storage[mobile] = {"otp": otp, "timestamp": time.time()}
            logging.info(f"OTP stored for {mobile}")

    def verify_otp(self, mobile: str, entered_otp: str) -> dict:
        """Verify the entered OTP for the given mobile number."""
        with self.lock:
            if mobile not in self.otp_storage:
                logging.warning(f"OTP not found or expired for {mobile}")
                return {"status": False, "message": "OTP not found or expired"}
            
            stored_otp_data = self.otp_storage[mobile]
            stored_otp = stored_otp_data["otp"]
            timestamp = stored_otp_data["timestamp"]

            # Check if OTP is expired (valid for 5 minutes)
            if time.time() - timestamp > 300:
                del self.otp_storage[mobile]
                logging.warning(f"OTP expired for {mobile}")
                return {"status": False, "message": "OTP has expired"}

            if entered_otp == stored_otp:
                del self.otp_storage[mobile]  # Clear OTP after successful verification
                logging.info(f"OTP verified successfully for {mobile}")
                return {"status": True, "message": "OTP verified successfully"}
            
            logging.warning(f"Invalid OTP entered for {mobile}")
            return {"status": False, "message": "Invalid OTP"}
