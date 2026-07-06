"""
test_api.py - Test the Resume Screening API
Run: python test_api.py
"""
import requests
import os
import tempfile

BASE_URL = "http://localhost:8000"

JOB_DESCRIPTION = """
Senior Python Backend Engineer

We are looking for a skilled Python developer to join our team.

Requirements:
- 5+ years of Python development experience
- Strong knowledge of FastAPI or Django REST Framework
- Experience with machine learning and NLP (scikit-learn, NLTK, spaCy)
- Proficiency in SQL and NoSQL databases (PostgreSQL, MongoDB)
- Docker and Kubernetes experience
- AWS or GCP cloud services
- Git version control
- RESTful API design
- Strong understanding of algorithms and data structures
- Experience with TF-IDF, cosine similarity, or other NLP techniques
- Agile/Scrum methodology experience

Nice to have:
- Experience with transformers and BERT models
- Redis caching
- CI/CD pipelines
"""

RESUME_ALICE = """
Alice Johnson
alice@email.com | +1-555-0101

SUMMARY
Senior Python Engineer with 7 years of experience building scalable backend systems.

SKILLS
Python, FastAPI, Django, scikit-learn, NLTK, spaCy, NLP, TF-IDF, Machine Learning,
PostgreSQL, MongoDB, Docker, Kubernetes, AWS, Redis, Git, REST APIs, Agile

EXPERIENCE
Senior Backend Engineer - TechCorp (2020-Present)
- Built NLP pipeline using TF-IDF and cosine similarity for document classification
- Developed FastAPI microservices deployed on AWS with Docker/Kubernetes
- Optimized PostgreSQL queries reducing latency by 60%

Python Developer - StartupXYZ (2018-2020)
- Developed machine learning models using scikit-learn
- Built REST APIs with Django REST Framework

EDUCATION
B.Sc Computer Science, MIT, 2018
"""

RESUME_BOB = """
Bob Smith
bob.smith@email.com

SUMMARY
Mid-level developer with 3 years experience in web development.

SKILLS
JavaScript, React, Node.js, Python basics, MySQL, Git

EXPERIENCE
Frontend Developer - WebAgency (2021-Present)
- Built React applications for e-commerce clients
- Worked with REST APIs

Junior Developer - LocalBiz (2020-2021)
- Maintained website and fixed bugs

EDUCATION
B.Sc Information Technology, 2020
"""

RESUME_CAROL = """
Carol Davis
carol.davis@email.com | +1-555-0303

SUMMARY
Data Scientist with 4 years of experience in machine learning and NLP.

SKILLS
Python, scikit-learn, NLTK, spaCy, TF-IDF, NLP, pandas, numpy,
Machine Learning, Deep Learning, PyTorch, SQL, Git, Jupyter

EXPERIENCE
Data Scientist - DataLab (2021-Present)
- Built text classification models using TF-IDF and BERT
- Developed NLP pipelines for information extraction
- Used cosine similarity for document ranking systems

ML Engineer - Analytics Corp (2020-2021)
- Developed recommendation systems with collaborative filtering
- Built APIs using Flask

EDUCATION
M.Sc Data Science, Stanford, 2020
"""


def create_temp_resume(content: str, filename: str) -> str:
    """Save resume text to a temp .txt file."""
    path = os.path.join(tempfile.gettempdir(), filename)
    with open(path, 'w') as f:
        f.write(content)
    return path


def test_health():
    print("Testing /api/health ...")
    r = requests.get(f"{BASE_URL}/api/health")
    print(f"  Status: {r.status_code} | Response: {r.json()}\n")


def test_screen():
    print("Testing /api/screen with 3 resumes ...")

    # Create temp resume files
    files_data = [
        ("alice_resume.txt", RESUME_ALICE),
        ("bob_resume.txt", RESUME_BOB),
        ("carol_resume.txt", RESUME_CAROL),
    ]

    temp_paths = []
    files = []
    for filename, content in files_data:
        path = create_temp_resume(content, filename)
        temp_paths.append(path)
        files.append(("resumes", (filename, open(path, "rb"), "text/plain")))

    try:
        response = requests.post(
            f"{BASE_URL}/api/screen",
            data={"job_description": JOB_DESCRIPTION},
            files=files,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Success! Screened {data['total_resumes']} resumes\n")
            print(f"  {'Rank':<6} {'Name':<20} {'File':<25} {'Score':>8} {'Label'}")
            print("  " + "-" * 70)
            for r in data['results']:
                print(f"  #{r['rank']:<5} {r['candidate_name']:<20} {r['filename']:<25} {r['score']:>7}% {r['score_label']}")
            print()
        else:
            print(f"  ❌ Error {response.status_code}: {response.text}\n")
    finally:
        for _, f_tuple in files:
            f_tuple[1].close()
        for p in temp_paths:
            os.unlink(p)


if __name__ == "__main__":
    print("=" * 60)
    print("AI Resume Screener - API Tests")
    print("=" * 60 + "\n")
    test_health()
    test_screen()
    print("Tests complete. Visit http://localhost:8000 for the UI.")
