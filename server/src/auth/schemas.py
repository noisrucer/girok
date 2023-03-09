from typing import Union
import datetime

from fastapi import HTTPException, status
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, validator, Field

import server.src.auth.exceptions as exceptions
import server.src.auth.enums as enums
import server.src.utils as utils
import server.src.user.schemas as user_schemas
    

class UserCreate(user_schemas.UserBase):
    password: str = Field(default=..., min_length=4, max_length=30)

    
class UserCreateOut(user_schemas.UserBase):
    user_id: int
    
    class Config:
        orm_mode = True
        
class VerifyEmail(BaseModel):
    email: str
    
    @validator('email')
    def email_must_be_valid(cls, v):
        try:
            validation = validate_email(v)
            email = validation.email
        except EmailNotValidError as e:
            raise exceptions.EmailNotValidException()
        return email
    
    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    
    
class ResetPasswordIn(BaseModel):
    new_password: str