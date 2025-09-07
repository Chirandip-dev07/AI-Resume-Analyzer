import streamlit as st
import pandas as pd
import os
from utils import extract_text_from_pdf, extract_entities, embed_text, load_skills, match_skills

# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📄 AI-Powered Resume Analyzer")
st.write("Upload your resume to extract insights, analyze skills, and match against job requirements.")

# -------------------------------
# Load Skills Dataset
# -------------------------------
skills_df = load_skills("skills.csv")
all_skills = skills_df["skill"].tolist() if skills_df is not None else []

# -------------------------------
# Sidebar for Uploads
# -------------------------------
st.sidebar.header("Upload Resume")
uploaded_file = st.sidebar.file_uploader("Upload a PDF Resume", type=["pdf"])

st.sidebar.header("Job Description")
job_description = st.sidebar.text_area(
    "Paste a Job Description",
    placeholder="Enter job description here..."
)

# -------------------------------
# Process Uploaded Resume
# -------------------------------
if uploaded_file is not None:
    with st.spinner("📑 Extracting text from resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    st.subheader("📜 Extracted Resume Text")
    st.write(resume_text[:1500] + "..." if len(resume_text) > 1500 else resume_text)

    # -------------------------------
    # Named Entity Recognition
    # -------------------------------
    with st.spinner("🔍 Performing Named Entity Recognition..."):
        entities = extract_entities(resume_text)

    st.subheader("🧩 Extracted Entities")
    st.json(entities)

    # -------------------------------
    # Skill Matching
    # -------------------------------
    if all_skills:
        with st.spinner("🎯 Matching skills with dataset..."):
            matched_skills = match_skills(resume_text, all_skills)

        st.subheader("💡 Matched Skills")
        st.write(", ".join(matched_skills) if matched_skills else "No skills matched.")

    # -------------------------------
    # Job Description Matching
    # -------------------------------
    if job_description:
        with st.spinner("🤖 Comparing resume with job description using embeddings..."):
            resume_emb = embed_text(resume_text)
            job_emb = embed_text(job_description)

            similarity = float(resume_emb @ job_emb.T)  # cosine similarity since SentenceTransformer outputs are normalized

        st.subheader("📊 Job Fit Score")
        st.metric(label="Similarity with Job Description", value=f"{similarity:.2f}")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("⚡ Built with Streamlit, spaCy, and SentenceTransformers")
