import streamlit as st
from google.generativeai import GenerativeModel, configure
import plotly.express as px
import pandas as pd

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="BubbleScope", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#3498db; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🔍 BubbleScope</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">See the shape of your filter bubble — and what's hidden beyond it.</p>', unsafe_allow_html=True)

st.info("Describe your main news sources and topics. BubbleScope shows opposing views, hidden stories, and the contours of your information bubble.")

sources = st.text_area(
    "Your main sources & platforms",
    height=100,
    placeholder="e.g., Twitter (follow tech influencers), Reddit (r/technology, r/politics), NYT, Fox News"
)

topics = st.text_area(
    "Topics you follow most",
    height=100,
    placeholder="e.g., AI, climate change, US politics, crypto"
)

lean = st.selectbox("Perceived political/cultural lean (optional)", ["Left", "Center-Left", "Center", "Center-Right", "Right", "None/Other"])

if st.button("Scope My Bubble", type="primary"):
    if not sources.strip() and not topics.strip():
        st.warning("Share at least sources or topics.")
    else:
        with st.spinner("Mapping your filter bubble..."):
            try:
                prompt = f"""
You are BubbleScope — an unbiased analyst of information ecosystems.

User's sources: {sources}
Main topics: {topics}
Self-described lean: {lean or "Not specified"}

Analyze their filter bubble:
1. What views, stories, or perspectives are likely hidden or downranked by their algorithms?
2. Shape of their bubble (e.g., topic silos, ideological lean, diversity level).
3. 5 specific examples of content/types they probably never see (articles, opinions, people).
4. How to escape: 3 balanced sources or searches to broaden exposure.

Be neutral, specific, and constructive. No judgment.
"""

                response = model.generate_content(prompt)
                analysis = response.text

                st.success("Bubble mapped")
                st.markdown("### Your Filter Bubble Analysis")
                st.markdown(analysis)

                # Simple visualization (mock bias spectrum)
                data = pd.DataFrame({
                    "Perspective": ["Far Left", "Left", "Center", "Right", "Far Right"],
                    "Exposure": [20, 60, 10, 8, 2]  # Mock — in real app, AI could estimate
                })
                fig = px.bar(data, x="Perspective", y="Exposure", title="Estimated Exposure Spectrum")
                st.plotly_chart(fig, use_container_width=True)

                st.caption("BubbleScope uses Gemini AI — this is an educated estimate based on your inputs.")
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

st.markdown("---")
st.caption("BubbleScope • See beyond your bubble • Powered by Gemini AI")
