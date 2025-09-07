# utils.py
import re
import pdfplumber
import docx2txt
import csv
from collections import Counter
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# load spaCy small model (english). Make sure requirements include spacy and en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    # When first running, user may need to run: python -m spacy download en_core_web_sm
    nlp = spacy.blank("en")

def extract_text_from_pdf(path):
    text_parts = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt:
                    text_parts.append(txt)
        return "\n".join(text_parts)
    except Exception as e:
        print("PDF extract error:", e)
        return ""

def extract_text_from_docx(path):
    try:
        text = docx2txt.process(path)
        if text:
            return text
        return ""
    except Exception as e:
        print("DOCX extract error:", e)
        return ""

def preprocess_text(text):
    # basic cleaning, lowercasing, remove extra whitespace and some symbols
    text = text.replace("\r", " ").replace("\n", " ").lower()
    text = re.sub(r"[^\w\s\-\+\.]", " ", text)  # allow dots, plus, hyphen
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_skills_list(csv_path="skills_list.csv"):
    skills = []
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    skills.append(row[0].strip().lower())
    except FileNotFoundError:
        # fallback sample
        skills = [
            "python", "java", "c++", "sql", "javascript", "react", "node", "flask",
            "django", "machine learning", "deep learning", "tensorflow", "pytorch",
            "nlp", "data analysis", "pandas", "numpy", "git", "docker", "kubernetes"
        ]
    return sorted(list(set([s for s in skills if s])))

def extract_skills_from_text(proc_text, skills_master):
    """
    Simple exact / substring matching of skills from skills_master.
    Returns found skills and mapping counts.
    """
    found = set()
    matches = Counter()
    # look for multi-word skills first
    text = proc_text.lower()
    for skill in sorted(skills_master, key=lambda x: -len(x)):
        if skill in text:
            found.add(skill)
            matches[skill] += text.count(skill)
    # Optionally use spaCy to find noun chunks / tokens
    doc = nlp(text)
    tokens = [tok.lemma_.lower() for tok in doc if not tok.is_stop and tok.is_alpha and len(tok) > 1]
    for skill in skills_master:
        # match by single token presence too
        if skill in found:
            continue
        parts = skill.split()
        if all(part in tokens for part in parts):
            found.add(skill)
            matches[skill] += 1
    return sorted(found), matches

def compute_keyword_match(job_proc, resume_proc, top_k=50):
    """
    Return a simple percent of job keywords present in resume.
    job_proc & resume_proc should be preprocessed text (lower).
    We'll extract candidate keywords from job_proc using TF-IDF (simple approach).
    """
    vect = TfidfVectorizer(stop_words="english", max_features=top_k)
    try:
        tfidf = vect.fit_transform([job_proc, resume_proc])
        feature_names = vect.get_feature_names_out()
        # find top features in job description by TF-IDF score
        job_vec = tfidf[0].toarray().ravel()
        top_idx = job_vec.argsort()[::-1][:top_k]
        job_keywords = [feature_names[i] for i in top_idx if job_vec[i] > 0]
        matched = []
        missing = []
        resume_tokens = set(resume_proc.split())
        for kw in job_keywords:
            if kw in resume_tokens:
                matched.append(kw)
            else:
                missing.append(kw)
        if len(job_keywords) == 0:
            pct = 0.0
        else:
            pct = 100.0 * len(matched) / len(job_keywords)
        return pct, matched, missing
    except Exception as e:
        print("Keyword match error:", e)
        return 0.0, [], []

def analyze_sections(raw_text):
    """
    Naive section detection using headings keywords.
    Returns dict: {'Summary': True/False, ...}
    """
    txt = raw_text.lower()
    sections = {
        "summary": False,
        "skills": False,
        "projects": False,
        "experience": False,
        "education": False,
        "certifications": False,
    }
    checks = {
        "summary": ["summary", "profile", "professional summary", "about me"],
        "skills": ["skills", "technical skills", "skills & technologies", "skillset"],
        "projects": ["projects", "personal projects", "academic projects"],
        "experience": ["experience", "work experience", "professional experience", "internship"],
        "education": ["education", "academic", "qualifications"],
        "certifications": ["certifications", "certified", "certificate"],
    }
    for sec, kws in checks.items():
        for k in kws:
            if k in txt:
                sections[sec] = True
                break
    return sections

def compute_formatting_score(raw_text):
    """
    Very naive formatting checks:
    - presence of contact info patterns (email, phone)
    - average line length (not too long)
    - presence of bullet points
    Returns a percentage 0-100
    """
    score = 0
    txt = raw_text
    # email
    if re.search(r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b", txt):
        score += 30
    # phone
    if re.search(r"(\+?\d[\d\-\s]{7,}\d)", txt):
        score += 20
    # bullets
    if re.search(r"•|-|\u2022", txt):
        score += 15
    # short lines: encourage concise bullets
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if lines:
        avg_len = sum(len(l) for l in lines) / len(lines)
        if avg_len < 120:
            score += 20
        elif avg_len < 200:
            score += 10
    # sections presence gives small bonus
    secs = analyze_sections(txt)
    present = sum(1 for v in secs.values() if v)
    score += min(present * 5, 15)
    return min(score, 100)

def compute_ats_score(skills_found, skills_master, keyword_match_pct=None, sections_present=None, raw_text=""):
    """
    Compose ATS score with weights:
    - Skills match -> 40%
    - Keywords match -> 30% (if JD provided)
    - Formatting -> 15%
    - Sections completeness -> 15%
    """
    # Skills matching: fraction of master skills found (cap)
    skills_master_set = set(skills_master)
    if skills_master_set:
        skills_score_raw = 100.0 * len([s for s in skills_found if s in skills_master_set]) / max(1, min(len(skills_master_set), 50))
        skills_pct = min(skills_score_raw, 100.0)
    else:
        skills_pct = 0.0

    # Keywords
    if keyword_match_pct is None:
        keywords_pct = 50.0  # unknown -> assume average
    else:
        keywords_pct = keyword_match_pct

    # formatting
    formatting_pct = compute_formatting_score(raw_text)

    # sections completeness
    if sections_present is None:
        sections_pct = 50.0
    else:
        # compute percent based on expected sections list
        expected = ["summary", "skills", "projects", "experience", "education"]
        present = sum(1 for s in expected if s in [x.lower() for x in sections_present])
        sections_pct = 100.0 * present / len(expected)

    total = (0.40 * skills_pct) + (0.30 * keywords_pct) + (0.15 * formatting_pct) + (0.15 * sections_pct)
    total_score = int(round(total))

    suggestions = []
    # suggestions based on simple heuristics
    if skills_pct < 40:
        suggestions.append("Add more relevant skills (technical keywords) up front in a Skills section.")
    if formatting_pct < 50:
        suggestions.append("Improve formatting: include contact info, bullet points, and shorter lines.")
    if sections_pct < 60:
        suggestions.append("Add or expand missing sections such as Summary, Projects, or Experience.")
    if keyword_match_pct is not None and keyword_match_pct < 50:
        suggestions.append("Tailor your resume to the job description: add keywords found in the job posting.")
    if len(raw_text.split()) > 1000:
        suggestions.append("Resume looks long — try to keep it concise (1-2 pages).")

    return {
        "skills_pct": skills_pct,
        "keywords_pct": keywords_pct,
        "formatting_pct": formatting_pct,
        "sections_pct": sections_pct,
        "total_score": total_score,
        "suggestions": suggestions,
    }
