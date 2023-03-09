from functools import lru_cache
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv('.env')


class JWTSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60*24*7
    
    class Config:
        env_file = ".env"
        

@lru_cache() 
def get_jwt_settings():
    return JWTSettings()