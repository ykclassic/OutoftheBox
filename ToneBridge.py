import streamlit as st
from google.generativeai import GenerativeModel, configure

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="ToneBridge", page_icon="🌍", layout="centered")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#3498db; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
    .culture-box { padding: 15px; border-radius: 10px; background: #2c3e50; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🌍 ToneBridge</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Not language translation — cultural intent translation for global teams.</p>', unsafe_allow_html=True)

st.info("Paste a message. ToneBridge shows how it lands in another culture and suggests better phrasing.")

# Culture options (common in global remote work)
cultures = [
    "United States", "Japan", "Germany", "India", "Brazil", "United Kingdom",
    "France", "China", "South Korea", "Mexico", "Netherlands", "Sweden",
    "Australia", "Canada", "Singapore", "Other"
]

col1, col2 = st.columns(2)
with col1:
    sender_culture = st.selectbox("Sender's cultural background", cultures, index=0)
with col2:
    receiver_culture = st.selectbox("Receiver's cultural background", cultures, index=1)

message = st.text_area("Message (e.g., Slack, email)", height=150, placeholder="We need this done by tomorrow.")

if st.button("Translate Tone", type="primary"):
    if not message.strip():
        st.warning("Enter a message first.")
    elif sender_culture == receiver_culture:
        st.info("Same culture selected — minimal translation needed, but here's a neutral analysis:")
    else:
        with st.spinner("Translating cultural intent..."):
            try:
                prompt = f"""
You are ToneBridge — an expert in cross-cultural communication for global remote teams.

Message: "{message}"
Sent from someone in: {sender_culture}
Received by someone in: {receiver_culture}

Analyze:
1. How does this message likely sound to the receiver? (direct, polite, rude, passive, urgent, etc.)
2. What intent does the sender probably have?
3. Are there cultural mismatches in tone, directness, hierarchy, or urgency?
4. Suggest 2-3 rephrased versions that preserve intent but land better in receiver's culture.
5. Flag any high-risk phrases.

Be specific, empathetic, and practical. Use real cultural communication norms.
"""

                response = model.generate_content(prompt)
                translation = response.text

                st.success("Cultural Translation Complete")
                st.markdown("### How This Message Lands")
                st.markdown(translation)

                st.caption("ToneBridge uses Gemini AI — always review for nuance. Not a substitute for cultural awareness.")
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

st.markdown("---")
st.caption("ToneBridge • Bridge cultures, not just words • Powered by Gemini AI")
