import streamlit as st
from google.generativeai import GenerativeModel, configure

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="FutureYou", page_icon="⏳", layout="centered")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#9b59b6; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
    .warning-box { background-color: #2c2c2c; padding: 20px; border-left: 6px solid #e74c3c; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">⏳ FutureYou</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Before sending that risky email — see how future you might regret it.</p>', unsafe_allow_html=True)

st.markdown("<div class='warning-box'>Paste a sensitive, emotional, or high-stakes email draft. FutureYou simulates how you'll feel reading it in the future.</div>", unsafe_allow_html=True)

email_draft = st.text_area("Email draft", height=200, placeholder="Paste your email here...")

col1, col2 = st.columns(2)
with col1:
    horizon_days = st.selectbox("Time horizon", [30, 90, 180, 365], index=1)
with col2:
    context = st.text_area("Optional context (relationship, stakes)", height=100, placeholder="e.g., This is to my boss after a bad review")

if st.button("Consult FutureYou", type="primary"):
    if not email_draft.strip():
        st.warning("Paste an email draft first.")
    else:
        with st.spinner(f"Channeling your self in {horizon_days} days..."):
            try:
                prompt = f"""
You are FutureYou — the user's self {horizon_days} days from now.

The user is about to send this email:
"{email_draft}"

Context: {context or "None provided"}

Your job:
- Imagine reading this email {horizon_days} days later.
- How would you feel? (regret, relief, embarrassment, pride?)
- What might have changed in that time?
- Rate regret risk: Low / Medium / High
- Suggest: send as-is, edit, or sleep on it

Be honest but kind. Speak as "I" (future self).
"""

                response = model.generate_content(prompt)
                future_view = response.text

                st.success("Message from FutureYou")
                st.markdown("### How I'll Feel About This Email")
                st.markdown(future_view)

                st.caption("FutureYou uses Gemini AI — this is a simulation to help you pause and reflect.")
            except Exception as e:
                st.error(f"Connection to future self failed: {str(e)}")

st.markdown("---")
st.caption("FutureYou • Pause before you send something you'll regret • Powered by Gemini AI")
