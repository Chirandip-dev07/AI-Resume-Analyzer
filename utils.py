# utils.py
import re
import pdfplumber
import docx2txt
import csv
from collections import Counter

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
    text = text.replace("\r", " ").replace("\n", " ").lower()
    text = re.sub(r"[^\w\s\-\+\.]", " ", text)
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
        # fallback
        skills = [
            "python", "java", "c++", "sql", "javascript", "react", "node",
            "flask", "django", "machine learning", "deep learning",
            "tensorflow", "pytorch", "nlp", "data analysis", "pandas",
            "numpy", "git", "docker", "kubernetes"
        ]
    return sorted(set(skills))

def extract_skills_from_text(proc_text, skills_master):
    found = set()
    matches = Counter()
    text = proc_text.lower()
    for skill in skills_master:
        if skill in text:
            found.add(skill)
            matches[skill] += text.count(skill)
    return sorted(found), matches

def analyze_sections(raw_text):
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
        "summary": ["summary", "profile", "about me"],
        "skills": ["skills", "technical skills"],
        "projects": ["projects", "personal projects"],
        "experience": ["experience", "work experience", "internship"],
        "education": ["education", "academic"],
        "certifications": ["certifications", "certificate"],
    }
    for sec, kws in checks.items():
        for k in kws:
            if k in txt:
                sections[sec] = True
                break
    return sections

def compute_formatting_score(raw_text):
    score = 0
    txt = raw_text
    if re.search(r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b", txt):
        score += 30
    if re.search(r"(\+?\d[\d\-\s]{7,}\d)", txt):
        score += 20
    if re.search(r"•|-|\u2022", txt):
        score += 15
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if lines:
        avg_len = sum(len(l) for l in lines) / len(lines)
        if avg_len < 120:
            score += 20
        elif avg_len < 200:
            score += 10
    secs = analyze_sections(txt)
    present = sum(1 for v in secs.values() if v)
    score += min(present * 5, 15)
    return min(score, 100)

def compute_ats_score(skills_found, skills_master, raw_text=""):
    skills_master_set = set(skills_master)
    if skills_master_set:
        skills_pct = 100.0 * len([s for s in skills_found if s in skills_master_set]) / max(1, len(skills_master_set))
    else:
        skills_pct = 0.0

    formatting_pct = compute_formatting_score(raw_text)

    sections_present = analyze_sections(raw_text)
    expected = ["summary", "skills", "projects", "experience", "education"]
    present = sum(1 for s in expected if sections_present.get(s, False))
    sections_pct = 100.0 * present / len(expected)

    total = (0.5 * skills_pct) + (0.3 * formatting_pct) + (0.2 * sections_pct)
    total_score = int(round(total))

    suggestions = []
    if skills_pct < 40:
        suggestions.append("Add more relevant technical skills.")
    if formatting_pct < 50:
        suggestions.append("Improve formatting: add contact info, bullet points, and concise lines.")
    if sections_pct < 60:
        suggestions.append("Add or expand missing sections like Summary, Projects, or Experience.")
    if len(raw_text.split()) > 1000:
        suggestions.append("Resume is too long — keep it within 1-2 pages.")

    return {
        "skills_pct": round(skills_pct, 1),
        "formatting_pct": formatting_pct,
        "sections_pct": sections_pct,
        "total_score": total_score,
        "suggestions": suggestions,
    }
