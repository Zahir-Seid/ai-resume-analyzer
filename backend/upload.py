from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse
import os
import requests
from datetime import datetime, timedelta
from auth import cookiejwtauth
from schemas import ResumeUpload, recent_uploads
from utils import create_token

router = APIRouter()

UPLOAD_DIR = "uploads"
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    token_data: dict = Depends(cookiejwtauth)
):
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Extract identity from token
        uploaded_by = token_data.get("sub", "anonymous")

        # Metadata to send with the file
        metadata = {
            "filename": filename,
            "original_filename": file.filename,
            "uploaded_by": uploaded_by,
            "uploaded_at": datetime.now().isoformat(),
        }

        # Save to recent uploads
        upload = ResumeUpload(
            filename=filename,
            original_filename=file.filename,
            uploaded_by=uploaded_by,
            uploaded_at=datetime.now(),
            status="processing"
        )
        recent_uploads.insert(0, upload)

        # Generate access token for n8n
        access_token = create_token({"sub": uploaded_by}, expires=timedelta(hours=1))

        # Send to n8n (multipart/form-data)
        with open(file_path, "rb") as f:
            files = {
                "file": (filename, f, "application/pdf")
            }
            data = metadata  # Sent as form-data fields
            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.post(N8N_WEBHOOK_URL, files=files, data=data, headers=headers, timeout=30)
            response.raise_for_status()
        
        upload.status = "success"
        return HTMLResponse(
            content="""
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
                <strong class="font-bold">Success!</strong>
                <span class="block sm:inline"> Resume uploaded and processing started.</span>
            </div>
            """,
            status_code=200
        )

    except requests.exceptions.RequestException as e:
        upload.status = "failed"
        return HTMLResponse(
            content=f"""
            <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative" role="alert">
                <strong class="font-bold">Warning!</strong>
                <span class="block sm:inline"> File uploaded but n8n processing failed: {str(e)}</span>
            </div>
            """,
            status_code=202
        )

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
