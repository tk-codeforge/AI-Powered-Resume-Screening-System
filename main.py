"""
main.py - FastAPI REST API for AI Resume Screening System
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.resume_parser import parse_resume
from app.scorer import score_resumes, get_score_label

# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Resume Screening System",
    description="NLP-based resume ranking using TF-IDF + Cosine Similarity",
    version="1.0.0",
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory="app/templates")

# ── Helper ────────────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}

def validate_file(filename: str):
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/screen")
async def screen_resumes(
    job_description: str = Form(..., description="Job description text"),
    resumes: list[UploadFile] = File(..., description="Resume files (PDF, DOCX, TXT)"),
):
    """
    Screen and rank resumes against a job description.

    - **job_description**: Full text of the job posting
    - **resumes**: One or more resume files

    Returns ranked list with scores and keyword analysis.
    """
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    if not resumes:
        raise HTTPException(status_code=400, detail="Please upload at least one resume.")

    # Save and parse resumes
    session_id = str(uuid.uuid4())[:8]
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    parsed_resumes = []
    errors = []

    for resume_file in resumes:
        validate_file(resume_file.filename)
        dest = session_dir / resume_file.filename
        try:
            with open(dest, "wb") as f:
                shutil.copyfileobj(resume_file.file, f)
            parsed = parse_resume(str(dest))
            parsed["filename"] = resume_file.filename
            parsed_resumes.append(parsed)
        except Exception as e:
            errors.append({"filename": resume_file.filename, "error": str(e)})
        finally:
            resume_file.file.close()

    if not parsed_resumes:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(status_code=422, detail=f"Could not parse any resume. Errors: {errors}")

    # Score resumes
    ranked = score_resumes(job_description, parsed_resumes)

    # Clean up uploaded files
    shutil.rmtree(session_dir, ignore_errors=True)

    # Build response
    results = []
    for r in ranked:
        results.append({
            "rank": r["rank"],
            "filename": r["filename"],
            "candidate_name": r.get("name") or "Unknown",
            "email": r.get("email"),
            "phone": r.get("phone"),
            "score": r["score"],
            "score_label": get_score_label(r["score"]),
            "keyword_match_rate": r["keyword_match_rate"],
            "matched_keywords": r["matched_keywords"],
            "missing_keywords": r["missing_keywords"],
            "word_count": r.get("word_count", 0),
        })

    return {
        "total_resumes": len(results),
        "errors": errors,
        "results": results,
    }


@app.post("/api/parse")
async def parse_single_resume(file: UploadFile = File(...)):
    """Parse a single resume and return extracted text + metadata."""
    validate_file(file.filename)
    temp_path = UPLOAD_DIR / f"temp_{uuid.uuid4().hex}_{file.filename}"
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        parsed = parse_resume(str(temp_path))
        parsed.pop("raw_text")  # Don't return full text in this endpoint
        parsed["filename"] = file.filename
        return parsed
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        file.file.close()
        temp_path.unlink(missing_ok=True)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/docs-ui", include_in_schema=False)
async def docs_redirect():
    return HTMLResponse('<meta http-equiv="refresh" content="0; url=/docs">')
