from fastapi import HTTPException, status


class EmailNotValidException(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "You must provide a valid email address type (ex. xxx@gmail.com)"
        
        
class EmailAlreadyExistsException(HTTPException):
    def __init__(self, email: str):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"Email: {email} already exists."
        
    
class CredentialsException(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Could not validate credentials"
        self.headers = {"WWW-Authenticate": "Bearer"}
        
        
class InvalidEmailOrPasswordException(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Incorrect email or password"
        self.headers = {"WWW-Authenticate": "Bearer"}
        
        
class AlreadyAuthenticationCodeSent(HTTPException):
    def __init__(self, email: str):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "The authentication code has already been sent."