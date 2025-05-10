import os
from jose import jwt, JWTError
from fastapi import Request, HTTPException, status
from fastapi.security.base import SecurityBase
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class CookieAuthModel(BaseModel):
    type_: str = "apiKey"
    in_: str = "cookie"
    name: str = "access_token"

class CookieJWTAuth(SecurityBase):
    def __init__(self, cookie_name: str = "access_token", auto_error: bool = True):
        self.model = CookieAuthModel(name=cookie_name)
        self.scheme_name = self.__class__.__name__
        self.auto_error = auto_error
        self.__fields__ = {}  

    async def __call__(self, request: Request) -> dict:
        token = request.cookies.get(self.model.name)
        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Authentication required"
                )
            raise ValueError("Missing access token")
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if "sub" not in payload:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token format"
                )
            return payload
        except JWTError as e:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Invalid credentials: {str(e)}"
                )
            raise

cookiejwtauth = CookieJWTAuth()