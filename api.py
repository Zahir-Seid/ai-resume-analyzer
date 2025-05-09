from fastapi import APIRouter, Request, HTTPException, Response, Depends, Form
from passlib.hash import bcrypt
from jose import jwt, JWTError
from datetime import timedelta
from auth import cookiejwtauth, SECRET_KEY, ALGORITHM
from schemas import LoginSchema, SignupSchema, TokenSchema, recent_uploads
from utils import get_conn, create_token
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

# Templates
templates = Jinja2Templates(directory="templates")

router = APIRouter()


# Signup
@router.post("/signup")
async def signup(payload: SignupSchema = Form(...)):
    conn = await get_conn()
    exists = await conn.fetchval("SELECT 1 FROM users WHERE email=$1", payload.email)
    if exists:
        await conn.close()
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed = bcrypt.hash(payload.password)
    await conn.execute("INSERT INTO users (email, password) VALUES ($1, $2)", payload.email, hashed)
    await conn.close()
    return {"message": "Registration successful"}

# Login
@router.post("/login")
async def login(payload: LoginSchema, response: Response):
    conn = await get_conn()
    user = await conn.fetchrow("SELECT * FROM users WHERE email=$1", payload.email)
    await conn.close()

    if not user or not bcrypt.verify(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token({"sub": user["email"]}, timedelta(minutes=60))
    refresh_token = create_token({"sub": user["email"]}, timedelta(days=7))

    response.set_cookie("access_token", access_token, httponly=True, max_age=3600)
    response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=7*24*60*60)

    return {"message": "Login successful", "access": access_token, "refresh": refresh_token}

# Logout
@router.post("/logout", dependencies=[Depends(cookiejwtauth)], include_in_schema=False)
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logout successful"}

# Refresh token
@router.post("/refresh-token")
async def refresh_token(request: Request):
    data = await request.json()
    refresh = data.get("refresh_token")
    if not refresh:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh, SECRET_KEY, algorithms=[ALGORITHM])
        new_access = create_token({"sub": payload["sub"]}, timedelta(minutes=60))
        return {"message": "Access token refreshed", "access": new_access}
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/uploads")
async def get_recent_uploads(request: Request, token_data: dict = Depends(cookiejwtauth), include_in_schema=False):
    # Return HTML for the recent uploads section
    html = """
    <div class="space-y-4">
        {% for upload in recent_uploads %}
        <div class="border rounded p-4">
            <div class="flex justify-between items-center">
                <div>
                    <h3 class="font-semibold">{{ upload.original_filename }}</h3>
                    <p class="text-sm text-gray-600">Uploaded by {{ upload.uploaded_by }}</p>
                </div>
                <div class="text-sm text-gray-500">
                    {{ upload.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') }}
                </div>
            </div>
            <div class="mt-2">
                <span class="px-2 py-1 text-xs rounded-full 
                    {% if upload.status == 'success' %}
                        bg-green-100 text-green-800
                    {% elif upload.status == 'processing' %}
                        bg-yellow-100 text-yellow-800
                    {% else %}
                        bg-red-100 text-red-800
                    {% endif %}">
                    {{ upload.status }}
                </span>
            </div>
        </div>
        {% endfor %}
    </div>
    """
    return templates.TemplateResponse(
        "recent_uploads.html",
        {"request": {}, "recent_uploads": recent_uploads}
    )