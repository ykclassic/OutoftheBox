import streamlit as st
from google.generativeai import GenerativeModel, configure
from fpdf2 import FPDF
import base64

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="FailForward", page_icon="🔥", layout="centered")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#ff4757; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🔥 FailForward</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Turn your failures into your greatest strengths.</p>', unsafe_allow_html=True)

st.info("List your mistakes, failures, and abandoned projects. FailForward will reframe them as learning, resilience, and risk tolerance — perfect for founders, creatives, and unconventional candidates.")

with st.form("failures_form"):
    st.markdown("### Your Failures & Mistakes")
    failures = st.text_area(
        "List everything you're 'not proud of' — failed startups, dropped projects, bad hires, wrong bets, public mistakes...",
        height=200,
        placeholder="e.g.,\n- Launched a product that got 0 users\n- Invested in crypto at the peak\n- Quit a stable job for an idea that flopped"
    )

    st.markdown("### Optional Context")
    context = st.text_area(
        "Add any brief notes (when it happened, what you learned, emotions at the time)",
        height=100,
        placeholder="e.g., 2021 crypto crash — lost 80%, felt devastated but learned about market cycles"
    )

    submitted = st.form_submit_button("Generate Reverse Resume")

if submitted:
    if not failures.strip():
        st.warning("Please share at least one failure.")
    else:
        with st.spinner("Reframing your failures into strengths..."):
            try:
                prompt = f"""
You are FailForward — a career coach for founders, creatives, and unconventional candidates.

The user has shared their failures and mistakes:
{failures}

Additional context:
{context or "None provided"}

Convert this into a professional 'reverse resume' that highlights:
- Key learnings and growth
- Resilience and adaptability
- Risk tolerance and bold thinking
- Pattern recognition and wisdom gained

Structure as a clean, positive resume section with:
- Bullet points
- Strong action verbs
- No judgment — only empowerment

Tone: Confident, authentic, inspiring.
"""

                response = model.generate_content(prompt)
                reverse_resume = response.text

                st.success("Reverse Resume Generated")
                st.markdown("### Your FailForward Profile")
                st.markdown(reverse_resume)

                # Fixed PDF Export using fpdf2
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "FailForward Profile", ln=1, align='C')
                pdf.ln(10)
                pdf.set_font("Arial", '', 12)

                # Write text line by line with proper encoding
                for line in reverse_resume.split('\n'):
                    cleaned_line = line.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 10, cleaned_line)

                # Get bytes directly
                pdf_bytes = pdf.output(dest='S')

                # Encode to base64
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

                st.download_button(
                    label="📥 Download as PDF",
                    data=pdf_base64,
                    file_name="failforward_profile.pdf",
                    mime="application/pdf"
                )

                st.caption("FailForward uses Gemini AI to reframe experience — this is your story, powerfully told.")
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")

st.markdown("---")
st.caption("FailForward • Your failures are your edge • Powered by Gemini AI")
