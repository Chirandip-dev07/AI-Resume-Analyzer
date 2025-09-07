import streamlit as st
import tempfile
import os
from utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    preprocess_text,
    load_skills_list,
    extract_skills_from_text,
    analyze_sections,
    compute_ats_score,
)

# App title
st.set_page_config(page_title="Tech Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 AI Tech Resume Analyzer")

st.markdown(
    """
Upload your resume and get an ATS-style analysis:
- ✅ Extracted text  
- 📊 Skills match  
- 🏗 Section completeness  
- 🎯 Overall ATS score with suggestions  
"""
)

# Upload resume
uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file is not None:
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Extract text
    if uploaded_file.name.endswith(".pdf"):
        raw_text = extract_text_from_pdf(tmp_path)
    else:
        raw_text = extract_text_from_docx(tmp_path)

    os.remove(tmp_path)

    if not raw_text.strip():
        st.error("❌ Could not extract text from the resume. Please try another file.")
    else:
        st.subheader("📑 Extracted Text")
        with st.expander("Show extracted text"):
            st.text(raw_text[:2000] + ("..." if len(raw_text) > 2000 else ""))

        # Preprocess
        proc_text = preprocess_text(raw_text)

        # Skills
        skills_master = load_skills_list()
        skills_found, matches = extract_skills_from_text(proc_text, skills_master)

        st.subheader("🛠 Skills Analysis")
        if skills_found:
            st.success(f"✅ Found {len(skills_found)} skills")
            st.write(", ".join(skills_found))
        else:
            st.warning("⚠ No relevant skills found. Try adding a clear Skills section.")

        # Sections
        sections = analyze_sections(raw_text)
        st.subheader("📂 Section Analysis")
        col1, col2 = st.columns(2)
        with col1:
            for sec, present in list(sections.items())[:3]:
                st.write(f"- **{sec.capitalize()}**: {'✅' if present else '❌'}")
        with col2:
            for sec, present in list(sections.items())[3:]:
                st.write(f"- **{sec.capitalize()}**: {'✅' if present else '❌'}")

        # ATS Score
        st.subheader("🎯 ATS Score")
        result = compute_ats_score(skills_found, skills_master, raw_text)
        st.metric("Overall ATS Score", f"{result['total_score']} / 100")

        st.progress(result["total_score"] / 100)

        # Sub-scores
        st.write("**Breakdown:**")
        st.write(f"- Skills Match: {result['skills_pct']:.1f}%")
        st.write(f"- Formatting: {result['formatting_pct']}%")
        st.write(f"- Sections Completeness: {result['sections_pct']}%")

        # Suggestions
        if result["suggestions"]:
            st.subheader("💡 Suggestions to Improve")
            for s in result["suggestions"]:
                st.write(f"- {s}")
        else:
            st.success("🎉 Your resume looks great! Minimal improvements needed.")


