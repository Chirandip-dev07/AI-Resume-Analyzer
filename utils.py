# utils.py

import re
import spacy
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load spaCy model for NER
nlp = spacy.load("en_core_web_sm")

# Load embeddings model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load skills list
skills_df = pd.read_csv("skills_list.csv")
skills_list = skills_df["skill"].str.lower().tolist()


# -------------------------
# Text Cleaning
# -------------------------
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)  # remove special chars
    text = re.sub(r"\s+", " ", text)  # collapse spaces
    return text.strip()


# -------------------------
# Extract Skills with Keyword + NER
# -------------------------
def extract_skills(text: str):
    doc = nlp(text)
    found_skills = set()

    # Keyword matching
    for token in text.split():
        if token.lower() in skills_list:
            found_skills.add(token.capitalize())

    # NER extraction (ORG, GPE, PERSON, etc.)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "SKILL"]:
            found_skills.add(ent.text)

    return list(found_skills)


# -------------------------
# Extract Sections (Summary, Education, etc.)
# -------------------------
def extract_sections(text: str):
    sections = {
        "summary": bool(re.search(r"(summary|objective)", text, re.IGNORECASE)),
        "education": bool(re.search(r"(education|b\.tech|m\.tech|bachelor|master)", text, re.IGNORECASE)),
        "skills": bool(re.search(r"(skills|technologies)", text, re.IGNORECASE)),
        "projects": bool(re.search(r"(projects|experience)", text, re.IGNORECASE)),
    }
    return sections


# -------------------------
# TF-IDF Keyword Matching
# -------------------------
def keyword_match(resume_text: str, job_text: str):
    documents = [resume_text, job_text]
    tfidf = TfidfVectorizer()
    matrix = tfidf.fit_transform(documents)
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return round(score * 100, 2)


# -------------------------
# Embedding Similarity (semantic)
# -------------------------
def embedding_similarity(resume_text: str, job_text: str):
    embeddings = embedder.encode([resume_text, job_text], convert_to_tensor=True)
    score = cosine_similarity(
        embeddings[0].cpu().numpy().reshape(1, -1),
        embeddings[1].cpu().numpy().reshape(1, -1)
    )[0][0]
    return round(score * 100, 2)


# -------------------------
# ATS Scoring
# -------------------------
def ats_score(resume_text: str, job_text: str):
    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_text)

    skills_found = extract_skills(resume_clean)
    sections = extract_sections(resume_text)

    # Subscores
    skill_match_score = keyword_match(resume_clean, job_clean) * 0.4
    embedding_score = embedding_similarity(resume_clean, job_clean) * 0.3
    section_score = (sum(sections.values()) / len(sections)) * 100 * 0.15
    formatting_score = 80 * 0.15  # Placeholder formatting score

    total = skill_match_score + embedding_score + section_score + formatting_score

    return {
        "total": round(total, 2),
        "skills_found": skills_found,
        "missing_sections": [k for k, v in sections.items() if not v],
        "subscores": {
            "skills": round(skill_match_score, 2),
            "semantic": round(embedding_score, 2),
            "sections": round(section_score, 2),
            "formatting": round(formatting_score, 2),
        },
    }
