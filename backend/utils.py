import asyncpg
from datetime import datetime, timedelta
from auth import SECRET_KEY, ALGORITHM
from jose import jwt
from dotenv import load_dotenv
import os
from asyncpg import Pool
import ssl 

load_dotenv()

# Token helpers
def create_token(data: dict, expires: timedelta):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + expires
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_conn():
    
    # Connection with SSL certificate
    return await asyncpg.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        ssl='require',  # Enable SSL for the connection
    )