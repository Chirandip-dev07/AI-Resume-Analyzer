import streamlit as st
from utils import (
    extract_text_from_pdf,
    extract_entities,
    embed_text,
    load_skills,
    match_skills,
    cosine_similarity,
)

# --- Streamlit page config ---
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Resume Analyzer")
st.write("Upload your resume to analyze ATS score, entities, and matched skills.")

# --- Sidebar upload ---
uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Extracting text..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    st.subheader("📑 Extracted Resume Text")
    with st.expander("Show full text"):
        st.write(resume_text)

    # --- NER Analysis ---
    st.subheader("🔍 Named Entity Recognition (NER)")
    entities = extract_entities(resume_text)
    if entities:
        st.write(pd.DataFrame(entities, columns=["Entity", "Label"]))
    else:
        st.info("No entities detected.")

    # --- Skills Match ---
    st.subheader("🛠 Skills Match")
    skills_list = load_skills("skills.csv")
    matched_skills = match_skills(resume_text, skills_list)
    st.write("**Matched Skills:**", ", ".join(matched_skills) if matched_skills else "None found")

    # --- Embeddings Similarity (Optional demo) ---
    st.subheader("📊 Embedding Similarity Demo")
    job_desc = st.text_area("Paste a Job Description to compare with your resume:")
    if job_desc:
        resume_vec = embed_text(resume_text)
        job_vec = embed_text(job_desc)
        similarity = cosine_similarity(resume_vec, job_vec)
        st.metric("Resume ↔ Job Description Similarity", f"{similarity:.2f}")

else:
    st.info("Please upload a resume PDF to begin analysis.")
