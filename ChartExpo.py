import streamlit as st
from google.generativeai import GenerativeModel, configure
import google.generativeai as genai

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

# Current multimodal model (vision-capable)
model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="ChartSkeptic", page_icon="📊", layout="centered")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#e74c3c; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">📊 ChartSkeptic</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Expose how charts mislead — intended story, hidden truths, deception tactics.</p>', unsafe_allow_html=True)

st.info("Upload a chart or dashboard screenshot. ChartSkeptic reveals what it's trying to sell you — and what it's hiding.")

uploaded_file = st.file_uploader("Upload chart image (PNG, JPG, PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if uploaded_file:
    # Display uploaded chart
    st.image(uploaded_file, caption="Uploaded Chart", use_column_width=True)

    with st.spinner("Skeptically analyzing the chart..."):
        try:
            # Fixed: Specify mime_type when uploading file-like object
            uploaded = genai.upload_file(uploaded_file, mime_type=uploaded_file.type)

            prompt = """
You are ChartSkeptic — a sharp, unbiased data visualization analyst for investors, journalists, and analysts.

Analyze this chart/dashboard critically:
1. What main story or message is the creator trying to convey?
2. How could this chart be misleading (e.g., truncated axes, cherry-picked data, confusing scaling, color manipulation)?
3. What important information might be hidden or downplayed unintentionally?
4. Rate deception risk: Low / Medium / High
5. Suggest questions a skeptic should ask

Be specific, evidence-based, and neutral. Reference visible elements (axes, labels, trends).
"""

            response = model.generate_content([uploaded, prompt])
            analysis = response.text

            st.success("Analysis complete")
            st.markdown("### ChartSkeptic Report")
            st.markdown(analysis)

            st.caption("ChartSkeptic uses Gemini AI vision — always verify with raw data. Not financial advice.")
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")

st.markdown("---")
st.caption("ChartSkeptic • See through the visualization • Powered by Gemini AI")
