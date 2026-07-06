# 🤖 AI Resume Screening System

An NLP-powered resume screening and candidate ranking system built with **FastAPI**, **TF-IDF**, and **Cosine Similarity**.

---

## ✨ Features

- 📄 **Multi-format Resume Parsing** — PDF, DOCX, DOC, TXT
- 🧠 **NLP Scoring** — TF-IDF + Cosine Similarity with NLTK preprocessing
- 🏆 **Automatic Ranking** — Rank 100+ candidates in seconds
- 🔑 **Keyword Analysis** — Matched & missing skills per candidate
- 🌐 **REST API** — FastAPI with auto-generated Swagger docs
- 💻 **Web UI** — Clean, dark-mode frontend included

---

## 📁 Project Structure

```
resume-screener/
├── main.py                  # FastAPI application & routes
├── app/
│   ├── resume_parser.py     # PDF/DOCX text extraction
│   ├── scorer.py            # TF-IDF + cosine similarity engine
│   └── templates/
│       └── index.html       # Web UI
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── test_api.py              # API test script
└── README.md
```

---

## 🚀 Deployment Guide

---

### Option 1 — Run Locally (Development)

**Step 1: Clone / navigate to project**
```bash
cd resume-screener
```

**Step 2: Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

**Step 3: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Start the server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Step 5: Open in browser**
```
http://localhost:8000           ← Web UI
http://localhost:8000/docs      ← Swagger API docs
```

---

### Option 2 — Docker (Recommended for Production)

**Step 1: Install Docker**
- Download from https://docs.docker.com/get-docker/

**Step 2: Build and run**
```bash
docker-compose up --build
```

**Step 3: Access the app**
```
http://localhost:8000
```

**Stop the container:**
```bash
docker-compose down
```

---

### Option 3 — Deploy to Railway (Free Cloud Hosting)

**Step 1: Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/resume-screener.git
git push -u origin main
```

**Step 2: Deploy on Railway**
1. Go to https://railway.app and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway auto-detects the Dockerfile and deploys
5. Click **"Generate Domain"** to get a public URL

---

### Option 4 — Deploy to Render (Free Tier)

**Step 1: Push to GitHub** (same as above)

**Step 2: Create a Render Web Service**
1. Go to https://render.com → **New → Web Service**
2. Connect your GitHub repo
3. Set:
   - **Environment**: Docker
   - **Port**: 8000
4. Click **"Create Web Service"**
5. Your app will be live at `https://your-app.onrender.com`

---

### Option 5 — Deploy to AWS EC2

**Step 1: Launch an EC2 instance**
- Go to AWS Console → EC2 → Launch Instance
- Choose Ubuntu 22.04, t2.micro (free tier)
- Open port 8000 in Security Group

**Step 2: SSH into the instance**
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

**Step 3: Install Docker**
```bash
sudo apt update && sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker ubuntu
```

**Step 4: Clone and run**
```bash
git clone https://github.com/YOUR_USERNAME/resume-screener.git
cd resume-screener
docker-compose up -d
```

**Step 5: Access the app**
```
http://YOUR_EC2_IP:8000
```

---

## 📡 API Reference

### `POST /api/screen`
Screen and rank multiple resumes against a job description.

**Request** (multipart/form-data):
| Field | Type | Description |
|-------|------|-------------|
| `job_description` | string | Full job posting text |
| `resumes` | file[] | One or more resume files |

**Response:**
```json
{
  "total_resumes": 3,
  "errors": [],
  "results": [
    {
      "rank": 1,
      "filename": "alice_resume.pdf",
      "candidate_name": "Alice Johnson",
      "email": "alice@email.com",
      "score": 78.45,
      "score_label": "Excellent Match",
      "keyword_match_rate": 72.0,
      "matched_keywords": ["python", "fastapi", "nlp", "docker"],
      "missing_keywords": ["kubernetes", "redis"]
    }
  ]
}
```

### `POST /api/parse`
Parse a single resume and extract metadata.

### `GET /api/health`
Health check endpoint.

---

## 🧪 Running Tests

```bash
# Make sure the server is running first
uvicorn main:app --reload

# In another terminal
python test_api.py
```

---

## 🔧 How It Works

1. **Upload** resumes (PDF/DOCX/TXT) + paste a job description
2. **Parser** extracts raw text from each file using `pdfplumber` / `python-docx`
3. **Preprocessor** cleans text — lowercase, remove stopwords, lemmatize with NLTK
4. **TF-IDF Vectorizer** converts all documents into numeric vectors
5. **Cosine Similarity** measures how similar each resume is to the JD
6. **Scorer** normalizes results to a 0–100% scale and extracts matched/missing keywords
7. **API** returns ranked results with explanations

---

## 📊 Score Labels

| Score | Label |
|-------|-------|
| ≥ 75% | Excellent Match |
| ≥ 55% | Good Match |
| ≥ 35% | Partial Match |
| < 35% | Low Match |
