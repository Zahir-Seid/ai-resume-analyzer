# Resume Analyzer API

A FastAPI-based backend service that integrates with n8n for automated resume analysis using AI.

## Features

- JWT-based authentication
- Secure PDF file upload
- Integration with n8n for automated processing
- PostgreSQL database for storing resume data
- Docker-based deployment

## Project Structure
``` bash
resume-analyzer/
├── backend/
│ ├── main.py
│ ├── api.py
│ ├── auth.py
│ ├── upload.py
│ ├── utils.py
│ ├── requirements.txt
│ └── Dockerfile
├── workflows/
│ └── resume_workflow.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## ⚙️ Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 🔐 Environment Variables

Create a `.env` file in the root directory based on `.env.example`:

```env
# Backend Configuration
SECRET_KEY=your-secret-key

# n8n Configuration (Cloud)
N8N_WEBHOOK_URL=https://your-n8n-cloud-url/webhook-test/xxxxxx
N8N_PROTOCOL=https

# PostgreSQL Configuration ()
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=your-db-name
DB_HOST=your-db-host
DB_PORT=your-db-port


```

## Setup and Running

1. Clone the repository:
```bash
git clone https://github.com/Zahir-Seid/ai-resume-analyzer
cd ai-resume-analyzer
```

2. Create and configure the `.env` file:
```bash
cp .env.example .env
# Edit .env with your values
```

3. Start the services:
```bash
docker-compose up -d
```
or :

```bash
sudo docker run -p 8000:8000 resume-analyzer
```
4. Access the services:
- FastAPI backend: http://localhost:8000/docs

# API Endpoints

## Authentication

| Method | Endpoint         | Description                | Auth  |
|--------|------------------|----------------------------|-------|
| POST   | `/login`    | Log in, returns JWT token  | No     |
| POST   | `/signup`   | Register a new user        | No    |
| POST   | `/logout`   | Invalidate the session     | yes   |

## Resume Upload

| Method | Endpoint    | Description             | Auth  |
|--------|-------------|-------------------------|-------|
| POST   | `/upload`   | Upload resume (PDF)     | yes   |
| GET    | `/uploads`  | List recent uploads     | yes   |

---

## How It Works

1. User authenticates and uploads a PDF resume.  
2. The backend saves the file and triggers an **n8n Cloud webhook** with metadata.  
3. The **n8n workflow**:
   - Extracts text from the PDF
   - Sends the text to an **AI agent** for information extraction
   - Saves the structured data to **PostgreSQL**
