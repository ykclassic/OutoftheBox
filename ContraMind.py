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

st.set_page_config(page_title="ContraMind", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#9b59b6; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
    .note-box { background-color: #2c3e50; padding: 15px; border-radius: 10px; margin: 10px 0; }
    .drift { background-color: #e74c3c; color: white; padding: 5px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🧠 ContraMind</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Your second brain that argues with you — keeping your thinking consistent.</p>', unsafe_allow_html=True)

st.info("Add your thoughts over time. ContraMind will challenge contradictions, flag belief drift, and highlight when you've changed your mind.")

# Initialize session state for notes
if 'notes' not in st.session_state:
    st.session_state.notes = []  # List of dicts: {'date': datetime, 'text': str}

# Sidebar: Add new note
with st.sidebar:
    st.header("Add a Thought")
    new_note = st.text_area("What do you believe or think right now?", height=150)
    note_date = st.date_input("When did you think this?", value=datetime.today())
    if st.button("Save Thought"):
        if new_note.strip():
            st.session_state.notes.append({
                "date": note_date.strftime("%Y-%m-%d"),
                "text": new_note.strip()
            })
            st.success("Thought saved!")
            st.rerun()
        else:
            st.warning("Write something first.")

# Main area
st.header("Your Knowledge Base")

if st.session_state.notes:
    # Sort by date
    sorted_notes = sorted(st.session_state.notes, key=lambda x: x['date'])

    for note in sorted_notes:
        with st.expander(f"{note['date']} — {note['text'][:100]}..."):
            st.write(note['text'])

    # AI Challenge Button
    if st.button("🧠 Have ContraMind Argue With Me", type="primary"):
        with st.spinner("Analyzing your beliefs for contradictions and drift..."):
            try:
                notes_text = "\n\n".join([f"{n['date']}: {n['text']}" for n in sorted_notes])

                prompt = f"""
You are ContraMind — a sharp, honest thinking partner.

Here are the user's past and present thoughts, ordered by date:
{notes_text}

Your job:
- Find direct contradictions (e.g., "You said X, but later said not X")
- Detect belief drift (gradual changes in opinion)
- Highlight unexamined assumptions or biases
- Point out when the user has wisely changed their mind

Be direct but kind. Use quotes from their notes.
Structure:
- Major Contradictions
- Belief Drift Over Time
- Key Insights / Growth

Speak directly: "You believed... but now you..."
"""

                response = model.generate_content(prompt)
                challenge = response.text

                st.success("ContraMind has thoughts")
                st.markdown("### ContraMind's Challenge")
                st.markdown(challenge)

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

    # Export
    export_data = json.dumps(st.session_state.notes, indent=2)
    st.download_button(
        "📥 Export All Notes (JSON)",
        export_data,
        "contramind_notes.json",
        "application/json"
    )
else:
    st.info("No thoughts yet. Add one in the sidebar to begin building your second brain.")

st.markdown("---")
st.caption("ContraMind • Your thinking, held accountable • Powered by Gemini AI")
