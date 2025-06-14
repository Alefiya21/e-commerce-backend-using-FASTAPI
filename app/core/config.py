import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
load_dotenv(override=True)

class Settings:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:12345@localhost/ecommerce_db")
    
    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Email
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
    # Reset token expiration (in minutes)
    RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings()