"""
scorer.py - TF-IDF + Cosine Similarity scoring engine
"""
import re
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK data (only needed once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

STOP_WORDS = set(stopwords.words('english'))
LEMMATIZER = WordNetLemmatizer()


def preprocess_text(text: str) -> str:
    """Clean and normalize text for NLP processing."""
    # Lowercase
    text = text.lower()
    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s\+\#]', ' ', text)
    # Tokenize
    tokens = text.split()
    # Remove stopwords and lemmatize
    tokens = [
        LEMMATIZER.lemmatize(t)
        for t in tokens
        if t not in STOP_WORDS and len(t) > 1
    ]
    return ' '.join(tokens)


def extract_keywords(text: str, top_n: int = 20) -> list[str]:
    """Extract top N keywords using TF-IDF on a single document."""
    processed = preprocess_text(text)
    vectorizer = TfidfVectorizer(max_features=top_n, ngram_range=(1, 2))
    try:
        tfidf_matrix = vectorizer.fit_transform([processed])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        sorted_idx = np.argsort(scores)[::-1]
        return [feature_names[i] for i in sorted_idx if scores[i] > 0][:top_n]
    except Exception:
        return processed.split()[:top_n]


def score_resumes(job_description: str, resumes: list[dict]) -> list[dict]:
    """
    Score and rank resumes against a job description.

    Args:
        job_description: Raw text of the job description
        resumes: List of dicts with keys: filename, raw_text, name, email, phone

    Returns:
        Sorted list of resumes with scores and matched keywords
    """
    if not resumes:
        return []

    # Preprocess all texts
    processed_jd = preprocess_text(job_description)
    processed_resumes = [preprocess_text(r['raw_text']) for r in resumes]

    # Build corpus: JD first, then resumes
    corpus = [processed_jd] + processed_resumes

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,  # Apply log normalization
        min_df=1
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Cosine similarity between JD (index 0) and each resume
    jd_vector = tfidf_matrix[0]
    resume_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(jd_vector, resume_vectors)[0]

    # Extract JD keywords for matching
    jd_keywords = set(extract_keywords(job_description, top_n=30))

    # Build results
    results = []
    for i, resume in enumerate(resumes):
        score = float(similarities[i])
        resume_keywords = set(extract_keywords(resume['raw_text'], top_n=30))
        matched = list(jd_keywords & resume_keywords)
        missing = list(jd_keywords - resume_keywords)

        results.append({
            **resume,
            "score": round(score * 100, 2),  # Convert to percentage
            "matched_keywords": matched[:15],
            "missing_keywords": missing[:10],
            "keyword_match_rate": round(len(matched) / max(len(jd_keywords), 1) * 100, 1),
        })

    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)

    # Add rank
    for i, r in enumerate(results):
        r['rank'] = i + 1

    return results


def get_score_label(score: float) -> str:
    """Return human-readable label for a score."""
    if score >= 75:
        return "Excellent Match"
    elif score >= 55:
        return "Good Match"
    elif score >= 35:
        return "Partial Match"
    else:
        return "Low Match"
