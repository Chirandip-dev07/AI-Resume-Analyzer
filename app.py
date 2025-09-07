import streamlit as st
from utils import extract_text_from_pdf, load_skills, match_skills

# --- Streamlit page config ---
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

st.title("📄 AI-Free Resume Analyzer")
st.write("Upload your resume to check ATS score, skills match, and section quality.")

# --- Sidebar upload ---
uploaded_file = st.sidebar.file_uploader("📂 Upload Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Extracting text..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    # --- Extracted Text ---
    st.subheader("📑 Extracted Resume Text")
    with st.expander("Show Full Text"):
        st.write(resume_text)

    # --- Skills Match ---
    st.subheader("🛠 Skills Analysis")
    skills_list = load_skills("skills.csv")
    matched_skills = match_skills(resume_text, skills_list)
    missing_skills = [s for s in skills_list if s.lower() not in resume_text.lower()]

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}")
    with col2:
        if missing_skills:
            st.warning(f"Missing Skills: {', '.join(missing_skills[:10])} ...")
        else:
            st.success("All key skills present!")

    # --- Section Completeness ---
    st.subheader("📋 Section Completeness")
    sections = {
        "Summary": "summary" in resume_text.lower(),
        "Skills": "skills" in resume_text.lower(),
        "Projects": "project" in resume_text.lower(),
        "Education": "education" in resume_text.lower(),
    }

    for section, present in sections.items():
        if present:
            st.success(f"{section}: ✅ Present")
        else:
            st.error(f"{section}: ❌ Missing")

    # --- ATS Score ---
    score = (len(matched_skills) * 2) + (sum(sections.values()) * 10)
    score = min(score, 100)

    st.subheader("📊 ATS Score")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("ATS Score", f"{score}/100")
    with col2:
        st.progress(score / 100)

    # --- Suggestions ---
    st.subheader("💡 Suggestions for Improvement")
    with st.expander("Show Suggestions"):
        if "summary" not in resume_text.lower():
            st.write("- Add a **Summary** section at the top.")
        if "skills" not in resume_text.lower():
            st.write("- Include a clear **Skills** section with bullet points.")
        if "project" not in resume_text.lower():
            st.write("- Highlight at least 2–3 **Projects** with impact.")
        if "education" not in resume_text.lower():
            st.write("- Add an **Education** section with degree and university details.")
        if len(matched_skills) < 5:
            st.write("- Mention more **job-relevant skills** to improve matching.")
        if score < 60:
            st.write("- Overall score is low. Try restructuring for better ATS compatibility.")

else:
    st.info("📂 Please upload a resume PDF to begin analysis.")
