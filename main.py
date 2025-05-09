from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from upload import router as upload_router
import os
import api
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Resume Analyzer API")

# CORS middleware — adjust origins if needed for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.com"],  # avoid ["*"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (e.g., uploaded resumes, frontend assets)
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")
# Register API routes
app.include_router(upload_router, tags=["Resume Uploads"])
app.include_router(api.router, tags=[" AI Resume analyzer"])

# Run server when called directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
