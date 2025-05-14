import random
import traceback
from app.core.config import settings
from loguru import logger
from fastapi import HTTPException
from twilio.rest import Client


def send_sms_or_call(mobile_number: str, message: str):
    try:
        client = Client(settings.senderid, settings.apikey)
        message = client.messages.create(
            body=message,
            from_=settings.sender_number,
            to=f"+91{mobile_number}")
        return {"data":{"message":"Otp Sent Sucessfully","status_code":200}}
    except Exception as e:
        logger.debug(traceback.format_exc())
        raise HTTPException(detail="Internal Server Error", status_code=500)
    # try:
    #     url = f"http://bsms.entrolabs.com/v3/api.php?username={settings.otp_username}&apikey={settings.apikey}&senderid={settings.senderid}&mobile={mobile_number}&message={message}"

    #     response = requests.request("GET", url)
    #     data = response.json()

    #     return {"data":{"message":"Otp Sent Sucessfully","status_code":200}}
    # except Exception as e:
    #     logger.debug(traceback.format_exc())
    #     raise HTTPException(detail="Internal Server Error", status_code=500)