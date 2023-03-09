from functools import lru_cache
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv('.env')


class EmailSettings(BaseSettings):
    GMAIL_SENDER: str
    GMAIL_APP_PASSWORD: str
    
    class Config:
        env_file = ".env"
        
        
@lru_cache()
def get_email_settings():
    return EmailSettings()