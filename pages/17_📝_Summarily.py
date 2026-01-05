import streamlit as st

# 1. Hide the standard menu and footer using CSS
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
from google.generativeai import GenerativeModel, configure
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import io

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Summarily", page_icon="📚", layout="wide")

# Fixed: Add unsafe_allow_html=True to ALL style/markdown with HTML/CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#3498db; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">📚 Summarily</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Chapter-by-chapter book summaries — upload or search.</p>', unsafe_allow_html=True)

mode = st.radio("How do you want to summarize?", ["Upload Book File", "Search by Details"])

if mode == "Upload Book File":
    st.header("Upload Your Book")
    uploaded_file = st.file_uploader("PDF, DOCX, or Image (scanned pages)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded File", use_column_width=True) if uploaded_file.type.startswith('image') else st.info("File uploaded")

        with st.spinner("Extracting and summarizing..."):
            try:
                gemini_file = genai.upload_file(uploaded_file, mime_type=uploaded_file.type)

                prompt = """
You are Summarily — an expert book summarizer.

This is a book file (PDF, DOCX, or scanned images).

Task:
- Identify chapters or major sections
- Summarize each chapter concisely (3-5 key points)
- Provide overall book summary and themes at the end
- Include key quotes if notable

Be accurate and insightful.
"""

                response = model.generate_content([gemini_file, prompt])
                summary = response.text

                st.success("Summary complete")
                st.markdown("### Chapter-by-Chapter Summary")
                st.markdown(summary)

            except Exception as e:
                st.error(f"Summarization failed: {str(e)}")

elif mode == "Search by Details":
    st.header("Search for Book Summary")
    title = st.text_input("Book Title (required)")
    author = st.text_input("Author Name (optional)")
    publisher = st.text_input("Publisher (optional)")
    pub_date = st.text_input("Publication Year (optional)")
    sample_lines = st.text_area("Few lines from any chapter (optional — helps accuracy)", height=100)

    if st.button("Generate Summary"):
        if not title.strip():
            st.warning("Title is required.")
        else:
            with st.spinner("Searching and summarizing..."):
                try:
                    prompt = f"""
You are Summarily — an expert book summarizer with knowledge of published books.

Book details:
Title: {title}
Author: {author or "Not provided"}
Publisher: {publisher or "Not provided"}
Publication year: {pub_date or "Not provided"}
Sample lines: {sample_lines or "None"}

Provide:
- Chapter-by-chapter summary (or major sections if non-fiction)
- Key themes, quotes, and takeaways
- Overall book message

If multiple editions exist, summarize the most common one.
If unsure or author missing, note limitations and do your best.

Structure clearly with headings.
"""

                    response = model.generate_content(prompt)
                    summary = response.text

                    st.success("Summary generated")
                    st.markdown("### Book Summary")
                    st.markdown(summary)

                except Exception as e:
                    st.error(f"Summarization failed: {str(e)}")

st.markdown("---")
st.caption("Summarily • Books distilled • Powered by Gemini AI")
