# app.py
import streamlit as st
from utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    preprocess_text,
    extract_skills_from_text,
    compute_keyword_match,
    compute_ats_score,
    analyze_sections,
    load_skills_list,
)
import tempfile
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objs as go

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

st.title("📄 AI-Powered Resume Analyzer — Starter")

# Load skills list
SKILLS_CSV = "skills_list.csv"
skills_master = load_skills_list(SKILLS_CSV)

col1, col2 = st.columns([1, 2])
with col1:
    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
    st.markdown("**Or** try sample resume in `sample_resumes/` (not included).")
with col2:
    job_desc = st.text_area(
        "Paste a Job Description (optional) — leave blank to analyze resume standalone",
        height=200,
    )

analyze_btn = st.button("🔎 Analyze Resume")

if analyze_btn:
    if not uploaded_file:
        st.error("Please upload a resume file (PDF or DOCX).")
        st.stop()

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    # Extract text
    if uploaded_file.type == "application/pdf" or tmp_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(tmp_path)
    else:
        text = extract_text_from_docx(tmp_path)

    if not text or len(text.strip()) < 10:
        st.warning("Couldn't extract meaningful text from the uploaded file.")
        st.stop()

    st.subheader("🔹 Raw Extracted Text (first 800 chars)")
    st.text_area("Extracted resume text", value=text[:800] + ("..." if len(text) > 800 else ""), height=200)

    # Preprocess
    proc_text = preprocess_text(text)

    # Section analysis
    sections = analyze_sections(text)
    st.subheader("📚 Section Check")
    sec_df = pd.DataFrame.from_dict(sections, orient="index", columns=["present"])
    sec_df["present"] = sec_df["present"].apply(lambda v: "✅" if v else "❌")
    st.table(sec_df)

    # Skills extraction
    found_skills, skill_matches = extract_skills_from_text(proc_text, skills_master)
    st.subheader(f"🧭 Skills Found ({len(found_skills)})")
    if found_skills:
        st.write(", ".join(sorted(found_skills)))
    else:
        st.write("_No skills detected using skills_list.csv seed._")

    # Keyword matching with job description (if provided)
    if job_desc and len(job_desc.strip()) > 5:
        job_proc = preprocess_text(job_desc)
        vectorizer = TfidfVectorizer().fit([proc_text, job_proc])
        vecs = vectorizer.transform([proc_text, job_proc])
        sim = cosine_similarity(vecs[0:1], vecs[1:2])[0][0]
        st.subheader("🔍 Resume ↔ Job Description Similarity")
        st.write(f"Cosine similarity (TF-IDF): **{sim:.3f}**")

        # compute per-keyword match (job keywords presence)
        job_keywords = [tok for tok in job_proc.split() if len(tok) > 2]
        keyword_score, matched, missing = compute_keyword_match(job_proc, proc_text)
        st.write(f"Keyword match score: **{keyword_score:.1f}%**")
        st.write("Top matched keywords (sample):", ", ".join(matched[:20]) if matched else "—")
        st.write("Top missing keywords (sample):", ", ".join(missing[:20]) if missing else "—")
    else:
        sim = None
        matched = []
        missing = []

    # ATS score
    ats = compute_ats_score(
        skills_found=found_skills,
        skills_master=skills_master,
        keyword_match_pct=keyword_score if job_desc else None,
        sections_present=[k for k, v in sections.items() if v],
        raw_text=text,
    )

    st.subheader("📊 ATS Score")
    st.write(f"**{ats['total_score']} / 100**")
    # Plot gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ats["total_score"],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "ATS Score"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "darkblue"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

    # Breakdown
    st.subheader("Breakdown")
    st.write(pd.DataFrame([
        {"metric": "Skills match (40%)", "score": f"{ats['skills_pct']:.1f}%"},
        {"metric": "Keywords match (30%)", "score": f"{ats['keywords_pct']:.1f}%"},
        {"metric": "Formatting (15%)", "score": f"{ats['formatting_pct']:.1f}%"},
        {"metric": "Sections completeness (15%)", "score": f"{ats['sections_pct']:.1f}%"},
    ]))

    # Suggestions
    st.subheader("💡 Improvement Suggestions")
    for s in ats["suggestions"]:
        st.write("- " + s)

    # Missing skills if job description provided
    if job_desc and missing:
        st.subheader("⚠️ Missing / Recommended Skills (based on JD)")
        missing_sample = missing[:40]
        st.write(", ".join(missing_sample))

    st.success("Analysis complete! Extend utils.py to add richer NER and embeddings.")
    