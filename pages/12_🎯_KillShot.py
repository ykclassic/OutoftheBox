import streamlit as st
from google.generativeai import GenerativeModel, configure

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="KillShot", page_icon="💀", layout="centered")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#e74c3c; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
    .warning-box { background-color: #2c2c2c; padding: 20px; border-left: 6px solid #e74c3c; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">💀 KillShot</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">The anti-pitch tool that tries to destroy your startup idea.</p>', unsafe_allow_html=True)

st.markdown("<div class='warning-box'>Warning: This tool is designed to be brutal. It assumes the role of a ruthless investor, competitor, and reality itself — all trying to kill your idea.</div>", unsafe_allow_html=True)

with st.form("idea_form"):
    st.markdown("### Your Startup Idea")
    idea_name = st.text_input("Idea name (optional)")
    description = st.text_area("What is the idea? (be specific)", height=150)
    
    st.markdown("### Key Details")
    col1, col2 = st.columns(2)
    with col1:
        target_users = st.text_input("Who is the target customer?")
        pricing = st.text_input("Pricing model")
    with col2:
        key_assumption = st.text_area("Biggest assumption you're making", height=100)
    
    submitted = st.form_submit_button("🔫 Fire KillShot", type="primary")

if submitted:
    if not description.strip():
        st.warning("Describe your idea first.")
    else:
        with st.spinner("Loading the firing squad..."):
            try:
                prompt = f"""
You are KillShot — a ruthless, no-mercy startup assassin.

Your job is to DESTROY this idea with cold, realistic criticism.
Idea: {idea_name or 'Unnamed'}
Description: {description}
Target users: {target_users}
Pricing: {pricing}
Key assumption: {key_assumption}

Attack from every angle:
- Why most users will be apathetic or ignore it
- Pricing resistance and willingness to pay
- Operational and execution failure points
- Competition and market timing
- Technical, legal, or distribution risks
- Founder blind spots

Rank the top 5 fatal flaws.
Give a survival probability (0-100%).
End with: if it somehow survives, one reason it might actually work.

Be brutal, specific, and evidence-based. No sugarcoating.
"""

                response = model.generate_content(prompt)
                kills = response.text

                st.success("Target eliminated... or is it?")
                st.markdown("### KillShot Report")
                st.markdown(kills)

                st.caption("KillShot uses Gemini AI to stress-test ideas — survive the critique, and your idea might be bulletproof.")
            except Exception as e:
                st.error(f"KillShot jammed: {str(e)}")

st.markdown("---")
st.caption("KillShot • Most ideas deserve to die • Powered by Gemini AI")
