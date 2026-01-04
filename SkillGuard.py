import streamlit as st
from google.generativeai import GenerativeModel, configure
from datetime import datetime
import json

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="SkillRust", page_icon="🛠️", layout="wide")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#e67e22; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
    .rust-low { background-color: #d4edda; padding: 10px; border-radius: 8px; }
    .rust-med { background-color: #fff3cd; padding: 10px; border-radius: 8px; }
    .rust-high { background-color: #f8d7da; padding: 10px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🛠️ SkillRust</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Track decaying skills and get quick refresh plans.</p>', unsafe_allow_html=True)

st.info("Add skills you haven't practiced. SkillRust estimates decay (heuristic) and gives time-efficient refresh plans.")

# Initialize session state
if 'skills' not in st.session_state:
    st.session_state.skills = []  # List of dicts: {'name': str, 'category': str, 'last_practiced': date, 'initial_level': int}

# Sidebar: Add skill
with st.sidebar:
    st.header("Add a Skill")
    skill_name = st.text_input("Skill name (e.g., Python, Calculus)")
    category = st.selectbox("Category", ["Coding", "Math", "Writing", "Language", "Music", "Sport", "Other"])
    last_practiced = st.date_input("Last practiced", value=datetime.today())
    initial_level = st.slider("Initial proficiency (1-10)", 1, 10, 8)
    
    if st.button("Add Skill"):
        if skill_name.strip():
            st.session_state.skills.append({
                "name": skill_name.strip(),
                "category": category,
                "last_practiced": last_practiced.strftime("%Y-%m-%d"),
                "initial_level": initial_level
            })
            st.success("Skill added!")
            st.rerun()

# Main area
st.header("Your Skills & Decay Status")

if st.session_state.skills:
    # Calculate days since last practiced
    today = datetime.today()
    for skill in st.session_state.skills:
        last_date = datetime.strptime(skill['last_practiced'], "%Y-%m-%d")
        days_inactive = (today - last_date).days
        
        # Heuristic decay (simple exponential — AI will refine)
        estimated_decay = min(100, days_inactive / 3)  # Rough % decay
        current_level = max(1, skill['initial_level'] - (estimated_decay / 20))

        risk_class = "rust-low" if estimated_decay < 30 else "rust-med" if estimated_decay < 70 else "rust-high"
        
        with st.expander(f"{skill['name']} ({skill['category']}) — Inactive: {days_inactive} days"):
            st.markdown(f"<div class='{risk_class}'>Estimated Decay: {estimated_decay:.0f}% | Current Level: {current_level:.1f}/10</div>", unsafe_allow_html=True)
            
            if st.button(f"Generate Refresh Plan for {skill['name']}", key=skill['name']):
                with st.spinner("Creating refresh plan..."):
                    try:
                        prompt = f"""
You are SkillRust — a pragmatic skill coach.

Skill: {skill['name']} ({skill['category']})
Last practiced: {skill['last_practiced']} ({days_inactive} days ago)
Initial proficiency: {skill['initial_level']}/10
Estimated current level: {current_level:.1f}/10

Create a time-optimized refresh plan to regain proficiency:
- Total time: under 5 hours spread over 1 week
- Focus on high-impact practice (not full mastery)
- Specific exercises or resources
- 3-5 short sessions

Be practical, encouraging, and realistic.
"""

                        response = model.generate_content(prompt)
                        plan = response.text

                        st.markdown("### Refresh Plan")
                        st.markdown(plan)
                    except Exception as e:
                        st.error(f"Plan generation failed: {str(e)}")

    # Export
    export_data = json.dumps(st.session_state.skills, indent=2)
    st.download_button(
        "📥 Export Skills (JSON)",
        export_data,
        "skillrust_data.json",
        "application/json"
    )
else:
    st.info("No skills tracked yet. Add one in the sidebar.")

st.markdown("---")
st.caption("SkillRust • Fight decay, reclaim your edge • Powered by Gemini AI")
