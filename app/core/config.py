import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mobile OTP Auth"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    otp_username: str = os.getenv("OTP_USERNAME")
    apikey: str = os.getenv("APIKEY")
    senderid: str = os.getenv("SENDERID")
    sender_number: str = os.getenv("SENDER_NUMBER")
    FB_CLIENT_ID: str = os.getenv("FB_CLIENT_ID")
    FB_CLIENT_SECRET: str = os.getenv("FB_CLIENT_SECRET")
    FB_REDIRECT_URI: str = os.getenv("FB_REDIRECT_URI")
    FB_AUTH_BASE: str = "https://www.facebook.com/v18.0/dialog/oauth"
    FB_TOKEN_URL: str = "https://graph.facebook.com/v18.0/oauth/access_token"
    GRAPH_API_BASE: str = "https://graph.facebook.com/v18.0"
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI")

    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    BUSINESS_PROFILE_API: str = "https://mybusinessbusinessinformation.googleapis.com/v1"
    OPEN_ROUTER_API_KEY: str = os.getenv("OPEN_ROUTER_API_KEY")
    OPEN_ROUTER_API: str = "https://openrouter.ai/api/v1/chat/completions"


    class Config:
        env_file = "app/.env"

settings = Settings()