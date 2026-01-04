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

st.info("Upload one or more chart/dashboard screenshots. ChartSkeptic analyzes each individually and, if multiple, compares them for consistency, correlation, or conflicts.")

uploaded_files = st.file_uploader(
    "Upload chart images (PNG, JPG, PDF)",
    type=['png', 'jpg', 'jpeg', 'pdf'],
    accept_multiple_files=True
)

if uploaded_files:
    uploaded_gemini_files = []
    analyses = []

    for idx, uploaded_file in enumerate(uploaded_files):
        st.markdown(f"### Chart {idx + 1}: {uploaded_file.name}")
        st.image(uploaded_file, use_column_width=True)

        with st.spinner(f"Analyzing Chart {idx + 1}..."):
            try:
                # Upload with mime_type
                gemini_file = genai.upload_file(uploaded_file, mime_type=uploaded_file.type)
                uploaded_gemini_files.append(gemini_file)

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

                response = model.generate_content([gemini_file, prompt])
                analysis = response.text
                analyses.append(analysis)

                st.success(f"Analysis complete for Chart {idx + 1}")
                st.markdown("#### Individual Report")
                st.markdown(analysis)

                st.markdown("---")  # Separator

            except Exception as e:
                st.error(f"Analysis failed for {uploaded_file.name}: {str(e)}")

    # === NEW: Multi-Chart Correlation/Comparison ===
    if len(uploaded_files) > 1:
        st.markdown("### Cross-Chart Comparison")
        with st.spinner("Comparing all charts for consistency, correlation, and conflicts..."):
            try:
                comparison_prompt = """
You are ChartSkeptic — analyzing multiple charts together.

Here are several charts/dashboards (uploaded as images).

Task:
1. Do these charts tell a consistent story, or are there contradictions?
2. Is there apparent correlation between trends shown (e.g., one variable driving another)?
3. Could the set of charts collectively be misleading (e.g., cherry-picking favorable views)?
4. Overall deception risk across the set: Low / Medium / High
5. Key insights or red flags when viewing them together

Be critical and specific.
"""

                # Send all uploaded files + prompt
                all_files_content = [file for file in uploaded_gemini_files]
                all_files_content.append(comparison_prompt)

                comparison_response = model.generate_content(all_files_content)
                comparison = comparison_response.text

                st.success("Cross-chart analysis complete")
                st.markdown(comparison)

            except Exception as e:
                st.error(f"Cross-chart comparison failed: {str(e)}")

    st.caption("ChartSkeptic uses Gemini AI vision — always verify with raw data. Not financial advice.")

st.markdown("---")
st.caption("ChartSkeptic • See through the visualization • Powered by Gemini AI")
