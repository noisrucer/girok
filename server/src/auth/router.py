from datetime import timedelta

from fastapi import APIRouter, status, Depends, BackgroundTasks
from email_validator import validate_email, EmailNotValidError
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import EmailStr


from server.src.database import get_db
import server.src.auth.schemas as schemas
import server.src.auth.exceptions as exceptions
import server.src.auth.service as service
import server.src.auth.utils as utils
import server.src.dependencies as glob_dependencies
import server.src.utils as glob_utils
import server.src.user.models as user_models
from server.src.auth.config import get_jwt_settings


jwt_settings = get_jwt_settings()

router = APIRouter(
    prefix="",
    tags=["auth"]
)


@router.post('/register/verify_email', status_code=status.HTTP_200_OK)
async def verify_email(user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user_dict = user.dict()
    
    # Check if there's a duplicated email in the DB
    if service.get_user_by_email(db, email=user_dict['email']):
        raise exceptions.EmailAlreadyExistsException(email=user_dict['email'])
    
    if service.get_pending_user_by_email(db, email=user_dict['email']):
        pending_registration = db.query(user_models.PendingRegistration).filter(user_models.PendingRegistration.email==user_dict['email']).first()
        db.delete(pending_registration)
        db.commit()
    
    try:
        validation = validate_email(user_dict['email'])
        email = validation.email
    except EmailNotValidError as e:
        raise exceptions.EmailNotValidException()
    
    # Send verification code
    verification_code = utils.generate_verification_code(len=6)
    recipient = email
    subject="[Girok] Please verify your email address"
    content = utils.read_html_content_and_replace(
        replacements={"__VERIFICATION_CODE__": verification_code},
        html_path="server/src/email/verification.html"
    )
    background_tasks.add_task(glob_utils.send_email, recipient, content, subject)
    
    # Hash password
    hashed_password = utils.hash_password(user_dict['password'])
    user_dict.update(password=hashed_password)
    user_dict.update(verification_code=verification_code)
    
    pending_user = user_models.PendingRegistration(**user_dict)
    
    db.add(pending_user)
    db.commit()
    
    return {"status": "successful", "verification_token": verification_code}


@router.post("/register/{verification_code}", status_code=status.HTTP_201_CREATED, response_model=schemas.UserCreateOut)
async def register(verification_code: str, db: Session = Depends(get_db)):
    pending_registration = db.query(user_models.PendingRegistration).filter(verification_code==verification_code).first()
    
    # Check if there's a duplicated email in the DB
    if service.get_user_by_email(db, email=pending_registration.email):
        raise exceptions.EmailAlreadyExistsException(email=pending_registration.email)
    
    user_dict = {"email": pending_registration.email,
                 "password": pending_registration.password}

    # Save to DB
    new_user = user_models.User(**user_dict)
    db.add(new_user)
    db.delete(pending_registration)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post('/login', response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
    user = service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise exceptions.InvalidEmailOrPasswordException()
        
    access_token_expires = timedelta(minutes=jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    # refresh_token_expires = timedelta(minutes=jwt_settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    # refresh_token = utils.create_refresh_token(
    #     data={"sub": user.email},
    #     expires_delta=refresh_token_expires
    # )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/validate-access-token", dependencies=[Depends(glob_dependencies.get_current_user)])
async def validate_jwt():
    return {"detail": "validated"}