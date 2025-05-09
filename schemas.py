from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class SignupSchema(BaseModel):
    username: str
    password: str

class LoginSchema(BaseModel):
    username: str
    password: str

class TokenSchema(BaseModel):
    refresh_token: str

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class ResumeUpload(BaseModel):
    filename: str
    original_filename: str
    uploaded_by: str
    uploaded_at: datetime
    status: str


# Mock database for recent uploads
recent_uploads: List[ResumeUpload] = []