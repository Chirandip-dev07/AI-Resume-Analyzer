import spacy
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd

# Lazy-loaded models
_nlp = None
_embedder = None

def get_nlp():
    """Load spaCy model only once."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp

def get_embedder():
    """Load SentenceTransformer model only once."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file."""
    import fitz  # PyMuPDF
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_entities(text):
    """Extract entities from text using spaCy NER."""
    nlp = get_nlp()
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def embed_text(text):
    """Return vector embedding for given text."""
    embedder = get_embedder()
    return embedder.encode(text)

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def load_skills(csv_path="skills.csv"):
    """Load skills from CSV file."""
    df = pd.read_csv(csv_path)
    return df["skill"].tolist()

def match_skills(resume_text, skills_list):
    """Match skills in resume against the skills list."""
    found = [skill for skill in skills_list if skill.lower() in resume_text.lower()]
    return found
