import streamlit as st
from google.generativeai import GenerativeModel, configure

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

# Use current stable model
model = GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Verdict", page_icon="⚖️", layout="centered")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#ff6b6b; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
    .question { font-size:18px; font-weight:bold; margin-top:30px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">⚖️ Verdict</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Evaluate the quality of your past decisions — not the outcome.</p>', unsafe_allow_html=True)

st.info("Verdict analyzes what you knew at the time, identifies biases and missing information, and judges if the decision was reasonable — even if things went wrong.")

with st.form("decision_form"):
    st.markdown("<p class='question'>1. What was the decision?</p>", unsafe_allow_html=True)
    decision = st.text_area("Describe the decision clearly (e.g., 'I invested in crypto in 2021', 'I took that job offer')", height=100)

    st.markdown("<p class='question'>2. When did you make it?</p>", unsafe_allow_html=True)
    when = st.text_input("Approximate date or year (e.g., 'March 2021', '2018')")

    st.markdown("<p class='question'>3. What was the actual outcome?</p>", unsafe_allow_html=True)
    outcome = st.text_area("Briefly describe what happened (good or bad)", height=100)

    st.markdown("<p class='question'>4. What did you know or believe at the time?</p>", unsafe_allow_html=True)
    knowledge = st.text_area("List key facts, beliefs, advice you had (or type 'I don’t remember much')", height=150)

    st.markdown("<p class='question'>5. What were your main goals or fears?</p>", unsafe_allow_html=True)
    goals = st.text_area("What were you hoping to achieve or avoid?", height=100)

    submitted = st.form_submit_button("Get Verdict")

if submitted:
    if not decision.strip():
        st.warning("Please describe the decision.")
    else:
        with st.spinner("Reconstructing your decision process..."):
            try:
                prompt = f"""
You are Verdict — a fair, empathetic decision analyst.

User's past decision:
- Decision: {decision}
- Made in: {when}
- Outcome: {outcome}
- Known at the time: {knowledge}
- Goals/fears: {goals}

Analyze this decision as if you are reviewing it WITHOUT hindsight.
Your job is to evaluate the QUALITY of the decision based ONLY on what was reasonably knowable at the time.

Step by step:
1. List the key assumptions the user likely made.
2. Identify information that was missing (but note if it was reasonably unknowable then).
3. Detect possible cognitive biases (e.g., overconfidence, anchoring, confirmation bias).
4. Consider personal and cultural context of that time.

Then give a clear verdict:
- Was this a reasonable decision given what was known?
- What made it strong or weak?
- One key lesson for future decisions.

Be kind, non-judgmental, and insightful. Use "you" to speak directly to the user.
"""

                response = model.generate_content(prompt)
                verdict = response.text

                st.success("Verdict complete")
                st.markdown("### Your Decision Autopsy")
                st.markdown(verdict)

                st.caption("Verdict uses AI to reconstruct mindset — this is an informed reflection, not absolute truth.")
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

st.markdown("---")
st.caption("Verdict • Judge the decision, not the outcome • Powered by Gemini AI")
