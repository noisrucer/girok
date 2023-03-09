import random
import string
from passlib.context import CryptContext
from jose import jwt, JWTError
from typing import Union
from datetime import datetime, timedelta

from server.src.auth.config import get_jwt_settings

jwt_settings = get_jwt_settings()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")


def hash_password(raw_password):
    return pwd_context.hash(raw_password)


def verify_password(raw_password, hashed_password):
    return pwd_context.verify(raw_password, hashed_password)


def generate_verification_code(len=6):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(len))


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
        
    to_encode.update({
        "exp": expire
    })
    encoded_jwt = jwt.encode(to_encode, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)
    return encoded_jwt


# def create_refresh_token(data: dict, expires_delta: Union[timedelta, None] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=60*24*7)
        
#     to_encode.update({
#         "exp": expire
#     })
#     encoded_jwt = jwt.encode(to_encode, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)
#     return encoded_jwt


def decode_jwt(token):
    payload = jwt.decode(token, jwt_settings.SECRET_KEY, algorithms=[jwt_settings.ALGORITHM])
    email: str = payload.get("sub")
    return email
    
    
def read_html_content_and_replace(
    replacements: dict[str, str],
    html_path: str = "server/src/email/verification.html"
):
    f = open(html_path)
    content = f.read()
    for target, val in replacements.items():
        content = content.replace(target, val)
    f.close()
    return content