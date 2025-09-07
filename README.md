# 📄 AI-Powered Resume Analyzer

**AI-Powered Resume Analyzer** is a web application that uses **natural language processing (NLP)** techniques to analyze resumes. It evaluates skills, section completeness, and formatting to provide an **ATS-style score** along with actionable suggestions for improvement.

---

## 🔹 Features

* **Resume Parsing**: Extracts text from PDF and DOCX resumes.
* **Skills Extraction**: Detects technical and soft skills from the resume.
* **Section Analysis**: Checks for key sections like Summary, Skills, Projects, Experience, Education.
* **ATS Scoring**: Calculates a comprehensive score (0–100) based on skills, keywords, formatting, and section completeness.
* **Suggestions**: Provides actionable tips to improve resume quality.
* **Dashboard-style UI**: Clean, dark-themed layout with columns for Skills, Sections, and Score.

---
## 🔹 Demo

[Live Demo on Streamlit Cloud](https://share.streamlit.io/yourusername/ai-resume-analyzer/main/app.py)


---

## 🔹 Tech Stack

* **Frontend**: Streamlit
* **Backend**: Python 3.x
* **NLP Libraries**: spaCy, sklearn, pdfplumber, docx2txt
* **Deployment**: Streamlit Cloud

---

## 🔹 Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the environment:

* **Windows (PowerShell)**:

```powershell
.\venv\Scripts\Activate.ps1
```

* **Mac/Linux**:

```bash
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the app:

```bash
streamlit run app.py
```

---

## 🔹 Usage

1. Upload your **resume** (PDF or DOCX) using the sidebar.
2. View **extracted text** in the expandable section.
3. Check **skills**, **sections**, and **ATS score** in the dashboard layout.
4. Review **suggestions** to improve your resume.

---

## 🔹 Project Structure

```
resume-analyzer/
│── app.py                  # Main Streamlit app
│── utils.py                # NLP helper functions
│── skills_list.csv         # Master skills database
│── requirements.txt        # Python dependencies
│── sample_resumes/         # Example resumes
│── .streamlit/config.toml  # Streamlit dark theme config
│── README.md               # Project documentation
```

---

## 🔹 How It Works

1. **Resume Parsing**: Reads PDF/DOCX files and extracts text.
2. **Preprocessing**: Lowercases text, removes symbols, tokenizes, and lemmatizes.
3. **Skills Extraction**: Matches extracted text with a predefined skills list.
4. **Section Analysis**: Detects key sections like Summary, Skills, Projects, etc.
5. **ATS Score Calculation**: Combines skills match, formatting, sections completeness, and keywords match to compute a score.
6. **Suggestions**: Provides personalized tips to improve resume quality.

---

## 🔹 Future Improvements

* Integrate **semantic similarity** with pre-trained models (BERT) for better keyword matching.
* Add **resume summary and bullet rewording** using AI models.
* Include **interactive charts** for skills and sections.
* Enhance UI with **external HTML/CSS dashboards**.

---

## 🔹 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 🔹 Acknowledgements

* [Streamlit](https://streamlit.io/) – for the web app framework
* [spaCy](https://spacy.io/) – for NLP
* [pdfplumber](https://github.com/jsvine/pdfplumber) – PDF text extraction
* [docx2txt](https://pypi.org/project/docx2txt/) – DOCX text extraction
