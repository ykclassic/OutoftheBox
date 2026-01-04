import streamlit as st
from google.generativeai import GenerativeModel, configure
from datetime import datetime

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="AssistForge", page_icon="🤝", layout="wide")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#3498db; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
    .task-card { background-color: #2c3e50; padding: 20px; border-radius: 10px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🤝 AssistForge</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Connect businesses with skilled virtual assistants for email, data entry, and more.</p>', unsafe_allow_html=True)

# Initialize session state for tasks
if 'tasks' not in st.session_state:
    st.session_state.tasks = []  # List of dicts

# Sidebar role selection
role = st.sidebar.radio("Your role", ["Business (post tasks)", "Virtual Assistant (find work)"])

if role == "Business (post tasks)":
    st.header("Post a Task")

    with st.form("post_task"):
        task_title = st.text_input("Task title", placeholder="e.g., Email management and calendar scheduling")
        description = st.text_area("Full description", height=150)
        skills = st.text_input("Required skills", placeholder="e.g., Gmail, Google Calendar, Excel")
        budget = st.number_input("Budget (USD per hour or fixed)", min_value=5.0, value=20.0)
        duration = st.text_input("Estimated duration", placeholder="e.g., 10 hours/week, ongoing")

        submitted = st.form_submit_button("Post Task")
        if submitted:
            st.session_state.tasks.append({
                "id": len(st.session_state.tasks) + 1,
                "title": task_title,
                "description": description,
                "skills": skills,
                "budget": budget,
                "duration": duration,
                "posted": datetime.now().strftime("%Y-%m-%d")
            })
            st.success("Task posted successfully!")

elif role == "Virtual Assistant (find work)":
    st.header("Available Tasks")

    if st.session_state.tasks:
        for task in st.session_state.tasks:
            with st.expander(f"Task #{task['id']}: {task['title']} — ${task['budget']}/hr — {task['duration']}"):
                st.write(f"**Description**: {task['description']}")
                st.write(f"**Skills needed**: {task['skills']}")
                st.write(f"**Posted**: {task['posted']}")

                if st.button(f"Apply to Task #{task['id']}", key=task['id']):
                    with st.spinner("Generating application suggestion..."):
                        try:
                            prompt = f"""
You are an expert virtual assistant applying for a task.

Task: {task['title']}
Description: {task['description']}
Skills: {task['skills']}
Budget/Duration: {task['budget']}, {task['duration']}

Write a short, professional application message (3-5 sentences) highlighting:
- Relevant experience
- Why you're a great fit
- Enthusiasm

Keep it concise and confident.
"""

                            response = model.generate_content(prompt)
                            suggestion = response.text

                            st.success("Application Suggestion")
                            st.markdown(suggestion)
                        except Exception as e:
                            st.error(f"Suggestion failed: {str(e)}")
    else:
        st.info("No tasks posted yet. Check back soon!")

st.markdown("---")
st.caption("AssistForge • Reliable virtual assistance, globally connected • Powered by Gemini AI")
