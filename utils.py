import asyncpg
from datetime import datetime, timedelta
from auth import SECRET_KEY, ALGORITHM
from jose import jwt

# Token helpers
def create_token(data: dict, expires: timedelta):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + expires
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# DB connection helper
async def get_conn():
    return await asyncpg.connect(user="postgres", password="password", database="resume_db", host="db")