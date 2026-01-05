import streamlit as st
from google.generativeai import GenerativeModel, configure
from PyPDF2 import PdfReader
from docx import Document
import json

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="GhostReply", page_icon="👻", layout="centered")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#95a5a6; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
    .warning-box { background-color: #2c2c2c; padding: 20px; border-left: 6px solid #95a5a6; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">👻 GhostReply</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Get the closure message they never sent — from their probable perspective.</p>', unsafe_allow_html=True)

st.markdown("<div class='warning-box'>This is an AI simulation for personal healing. It's not real contact and not guaranteed accurate — use for reflection only.</div>", unsafe_allow_html=True)

st.info("Upload old messages/emails from someone who ghosted you. GhostReply writes the unsent reply to help you move on.")

uploaded_files = st.file_uploader(
    "Upload conversation history (TXT, PDF, DOCX, JSON email exports)",
    type=['txt', 'pdf', 'docx', 'json'],
    accept_multiple_files=True
)

relationship = st.selectbox("Relationship type", ["Friend", "Romantic/Dating", "Colleague/Professional", "Family", "Other"])

reason_guess = st.text_area(
    "Why do you think they ghosted? (optional — helps AI perspective)",
    height=100,
    placeholder="e.g., They got busy with work, fear of confrontation, lost interest"
)

tone = st.selectbox("Desired tone of their reply", ["Apologetic & Kind", "Honest & Explanatory", "Neutral & Detached", "Regretful"])

if st.button("Generate GhostReply", type="primary"):
    if not uploaded_files:
        st.warning("Upload at least one conversation file.")
    else:
        all_text = ""
        for file in uploaded_files:
            content = ""
            if file.type == "text/plain":
                content = file.read().decode("utf-8", errors="ignore")
            elif file.type == "application/pdf":
                try:
                    reader = PdfReader(file)
                    content = "\n".join([page.extract_text() or "" for page in reader.pages])
                except:
                    content = "[Error reading PDF]"
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                try:
                    doc = Document(file)
                    content = "\n".join([para.text for para in doc.paragraphs])
                except:
                    content = "[Error reading DOCX]"
            elif file.type == "application/json":
                try:
                    data = json.load(file)
                    content = str(data)
                except:
                    content = "[Error reading JSON]"

            all_text += f"\n\n--- From {file.name} ---\n{content[:15000]}"

        if all_text.strip():
            with st.spinner("Channeling their unsent reply..."):
                try:
                    prompt = f"""
You are GhostReply — writing the closure message that a person who ghosted someone would send if they finally explained themselves.

Relationship: {relationship}
User's guess why ghosted: {reason_guess or "Not provided"}
Desired tone: {tone}

Conversation history:
{all_text[:20000]}

Write the message as if from their perspective ("I" = the ghoster).
- Explain why they disappeared
- Acknowledge impact
- Offer closure
- Keep tone: {tone.lower()}

Be realistic, human, and empathetic — not perfect or overly polished.
Keep it concise (200-400 words).
"""

                    response = model.generate_content(prompt)
                    reply = response.text

                    st.success("Message from the ghost")
                    st.markdown("### The Unsent Reply")
                    st.markdown(reply)

                    st.caption("GhostReply uses Gemini AI — this is a simulation for personal closure. It's not real and not guaranteed accurate.")
                except Exception as e:
                    st.error(f"Generation failed: {str(e)}")
        else:
            st.warning("No readable text found in files.")

st.markdown("---")
st.caption("Ghostly • Get the conversation you never had • Powered by ForgeAI")
