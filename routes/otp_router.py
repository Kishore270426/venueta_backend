import phonenumbers
from fastapi import APIRouter, HTTPException
from schemas.otp_schemas import MobileRequest, OTPRequest
from services.otp_service import OTPService
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter()

otp_service = OTPService()


def validate_phone_number(mobile: str) -> str:
    """Validate and format the mobile number to E.164 format."""
    try:
        parsed_number = phonenumbers.parse(mobile, None)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError("Invalid phone number")
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
    except Exception as e:
        logging.error(f"Phone number validation failed for {mobile}: {e}")
        raise HTTPException(status_code=400, detail="Invalid phone number format")


@router.post("/send-otp")
async def send_otp(request: MobileRequest):
    try:
        # Validate the phone number
        mobile = validate_phone_number(request.mobile)
        logging.info(f"Validated phone number: {mobile}")

        # Generate and send OTP
        otp = otp_service.generate_otp()
        otp_service.store_otp(mobile, otp)
        otp_service.send_otp(mobile, otp)

        logging.info(f"OTP sent successfully to {mobile}")
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error occurred while sending OTP to {request.mobile}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP. Please try again later.")

    return {"message": "OTP sent successfully"}

@router.post("/verify-otp")
async def verify_otp_endpoint(request: OTPRequest):
    try:
        # Validate phone number and format it to E.164
        mobile = validate_phone_number(request.mobile)
        logging.info(f"Validated phone number for OTP verification: {mobile}")

        # Verify OTP
        result = otp_service.verify_otp(mobile, request.otp)

        if result["status"]:
            logging.info(f"OTP successfully verified for {mobile}")
            return {"message": result["message"]}
        else:
            logging.error(f"OTP verification failed for {mobile}: {result['message']}")
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        logging.error(f"Error occurred during OTP verification: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify OTP. Please try again later.")
