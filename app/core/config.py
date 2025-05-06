import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Mobile OTP Auth"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "1234")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "database")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    ALGORITHM = "HS256"
    otp_username = os.getenv("OTP_USERNAME", "ClickSeek")
    apikey = os.getenv("APIKEY", "6e9ebca80ffb5cd0e0808e99b59ef192")
    senderid = os.getenv("SENDERID", "AC073263636ee4ffebb25c2b529b24084a")
    sender_number = os.getenv("SENDER_NUMBER", "+19786783493")

settings = Settings()