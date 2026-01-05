import streamlit as st
from google.generativeai import GenerativeModel, configure

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="RegretMirror", page_icon="🪞", layout="centered")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#8e44ad; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
    .warning-box { background-color: #2c2c2c; padding: 20px; border-left: 6px solid #8e44ad; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🪞 RegretMirror</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">See your life from the deathbed — what you'll regret, what you'll be proud of.</p>', unsafe_allow_html=True)

st.markdown("<div class='warning-box'>This app simulates your future self at the end of life reflecting on today's choices. It's inspired by real regrets of the dying — use it for clarity, not fear.</div>", unsafe_allow_html=True)

priorities = st.text_area(
    "Your current priorities (what matters most right now)",
    height=150,
    placeholder="e.g., Career success, family time, health, creative projects, financial security"
)

habits = st.text_area(
    "Your daily habits and routine",
    height=150,
    placeholder="e.g., Work 10 hours/day, scroll social media 2 hours, exercise 3x/week, family dinner most nights"
)

if st.button("Show Me the Mirror", type="primary"):
    if not priorities.strip() or not habits.strip():
        st.warning("Share both priorities and habits for a meaningful reflection.")
    else:
        with st.spinner("Reflecting from the end..."):
            try:
                prompt = f"""
You are RegretMirror — speaking as the user's future self on their deathbed, looking back.

Current priorities: {priorities}
Daily habits: {habits}

Reflect honestly but kindly:
- Which of today's choices will I likely regret? (reference common deathbed regrets: not living true to self, working too hard, not expressing feelings, losing touch with friends, not allowing happiness)
- Which choices will I be proud of and grateful for?
- What small adjustments today would make the biggest difference?

Speak as "I" (future self). Be profound, empathetic, and specific.
Structure: Opening reflection + Regrets + Pride + Gentle advice.
"""

                response = model.generate_content(prompt)
                reflection = response.text

                st.success("Message from your future self")
                st.markdown("### RegretMirror Reflection")
                st.markdown(reflection)

                st.caption("RegretMirror uses Gemini AI — inspired by Bronnie Ware's Top 5 Regrets of the Dying. This is a simulation for perspective.")
            except Exception as e:
                st.error(f"Reflection failed: {str(e)}")

st.markdown("---")
st.caption("RegretMirror • Live without regret • Powered by Gemini AI")
