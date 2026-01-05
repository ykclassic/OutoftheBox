import streamlit as st
from google.generativeai import GenerativeModel, configure
from PyPDF2 import PdfReader
from docx import Document

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="ClearPact", page_icon="📄", layout="wide")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#3498db; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
    .risk-low { background-color: #d4edda; padding: 10px; border-radius: 8px; margin: 10px 0; }
    .risk-med { background-color: #fff3cd; padding: 10px; border-radius: 8px; margin: 10px 0; }
    .risk-high { background-color: #f8d7da; padding: 10px; border-radius: 8px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">📄 ClearPact</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Contracts in plain English + risk visualized</p>', unsafe_allow_html=True)

st.info("Upload any contract. ClearPact rewrites it in simple language, highlights risk zones, and shows who benefits most in each section.")

uploaded_file = st.file_uploader("Upload contract (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])

if uploaded_file:
    # Extract text
    text = ""
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif uploaded_file.type == "text/plain":
        text = uploaded_file.read().decode("utf-8")

    if text.strip():
        with st.spinner("Analyzing contract..."):
            try:
                prompt = f"""
You are ClearPact — a legal expert who translates contracts into plain English and analyzes risk.

Contract text:
{text[:30000]}  # Truncate if too long

Task:
1. Rewrite the entire contract in simple, clear English (keep structure with section headings).
2. For each major section, add:
   - Risk level: Low / Medium / High
   - Who benefits most: Party A / Party B / Balanced / Unclear
   - Brief reason (1 sentence)

Output format:
- Use markdown headings for sections
- After each section, add tags like:
  **Risk: High** | **Favors: Party A** | Reason: One-sided termination rights

Be accurate, neutral, and helpful.
"""

                response = model.generate_content(prompt)
                analysis = response.text

                st.success("Analysis complete")
                st.markdown("### Plain English Contract + Risk Heatmap")
                st.markdown(analysis)

                # Simple download (HTML for now)
                html = f"<pre>{analysis}</pre>"
                st.download_button(
                    "📥 Download Analysis",
                    html,
                    "clearpact_analysis.html",
                    "text/html"
                )

                st.caption("ClearPact uses Gemini AI — review all outputs carefully. Not legal advice.")
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
    else:
        st.warning("No text extracted from file.")

st.markdown("---")
st.caption("ClearPact • Contracts made human • Powered by Gemini AI")
