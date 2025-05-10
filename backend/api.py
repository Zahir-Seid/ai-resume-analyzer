from fastapi import APIRouter, Request, HTTPException, Response, Depends, Form
from passlib.hash import bcrypt
from jose import jwt, JWTError
from datetime import timedelta
from auth import cookiejwtauth, SECRET_KEY, ALGORITHM
from schemas import LoginSchema, SignupSchema, TokenSchema, recent_uploads
from utils import get_conn, create_token
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

# Templates
templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
def get_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# Signup
@router.post("/signup")
async def signup(payload: SignupSchema = Form(...)):
    conn = await get_conn()
    exists = await conn.fetchval("SELECT 1 FROM users WHERE username=$1", payload.username)
    if exists:
        await conn.close()
        raise HTTPException(status_code=400, detail="username already exists")

    hashed = bcrypt.hash(payload.password)
    await conn.execute("INSERT INTO users (username, password) VALUES ($1, $2)", payload.username, hashed)
    await conn.close()
    response = JSONResponse(content={"message": "Registration successful"})
    response.headers["HX-Redirect"] = "/login"
    return response

# Login
@router.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    conn = await get_conn()
    user = await conn.fetchrow("SELECT * FROM users WHERE username=$1", username)
    await conn.close()

    if not user or not bcrypt.verify(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token({"sub": user["username"]}, timedelta(minutes=60))
    refresh_token = create_token({"sub": user["username"]}, timedelta(days=7))

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        max_age=3600, # 1hr
        secure=False,  
        samesite="Lax"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=False,
        max_age=604800,  # 7 days
        secure=False,
        samesite="Lax"
    )

    # Add redirect header to the same response
    response.headers["HX-Redirect"] = "/"
    return {"message": "Login successful"}

# Logout
@router.post("/logout", dependencies=[Depends(cookiejwtauth)])
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logout successful"}

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, token_data: dict = Depends(cookiejwtauth)):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/uploads")
async def get_recent_uploads(request: Request, token_data: dict = Depends(cookiejwtauth)):
    return templates.TemplateResponse(
        "recent_uploads.html",
        {"request": request, "recent_uploads": recent_uploads}
    )