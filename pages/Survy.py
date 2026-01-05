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

st.set_page_config(page_title="SurveyForge", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#2ecc71; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">📊 SurveyForge</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Automated surveys with AI-powered insights for businesses.</p>', unsafe_allow_html=True)

st.info("Create a survey, collect responses, and get AI insights on customer feedback.")

# Initialize session state
if 'surveys' not in st.session_state:
    st.session_state.surveys = {}  # {survey_id: {'title': str, 'questions': list, 'responses': list}}

tab1, tab2, tab3 = st.tabs(["Create Survey", "Take Survey", "View Insights"])

with tab1:
    st.header("Create a New Survey")
    survey_title = st.text_input("Survey Title")
    
    questions = []
    st.markdown("### Add Questions")
    num_questions = st.number_input("Number of questions", min_value=1, max_value=10, value=3)
    
    for i in range(num_questions):
        q_text = st.text_input(f"Question {i+1}")
        q_type = st.selectbox(f"Type for Q{i+1}", ["Text", "Multiple Choice"], key=f"type_{i}")
        if q_type == "Multiple Choice":
            options = st.text_area(f"Options for Q{i+1} (one per line)", key=f"options_{i}")
            options_list = [opt.strip() for opt in options.split("\n") if opt.strip()]
        else:
            options_list = None
        if q_text:
            questions.append({"text": q_text, "type": q_type, "options": options_list})

    if st.button("Create Survey"):
        if survey_title and questions:
            survey_id = len(st.session_state.surveys) + 1
            st.session_state.surveys[survey_id] = {
                "title": survey_title,
                "questions": questions,
                "responses": []
            }
            st.success(f"Survey '{survey_title}' created! ID: {survey_id}")
            st.info(f"Share this link: https://your-app-url?survey={survey_id} (mock for MVP)")

with tab2:
    st.header("Take a Survey")
    survey_id = st.text_input("Enter Survey ID")
    if survey_id and survey_id.isdigit() and int(survey_id) in st.session_state.surveys:
        survey = st.session_state.surveys[int(survey_id)]
        st.markdown(f"### {survey['title']}")
        
        responses = {}
        for idx, q in enumerate(survey['questions']):
            if q['type'] == "Text":
                responses[idx] = st.text_area(q['text'], key=f"resp_{survey_id}_{idx}")
            else:
                responses[idx] = st.radio(q['text'], q['options'], key=f"resp_{survey_id}_{idx}")

        if st.button("Submit Response"):
            st.session_state.surveys[int(survey_id)]['responses'].append(responses)
            st.success("Response submitted! Thank you.")

with tab3:
    st.header("View Survey Insights")
    survey_id = st.selectbox("Select Survey", options=list(st.session_state.surveys.keys()), format_func=lambda x: st.session_state.surveys[x]['title'])
    
    if survey_id:
        survey = st.session_state.surveys[survey_id]
        responses = survey['responses']
        
        st.markdown(f"### {survey['title']} — {len(responses)} responses")
        
        if responses:
            with st.spinner("Generating AI insights..."):
                try:
                    # Format responses for AI
                    formatted_responses = ""
                    for idx, resp in enumerate(responses):
                        formatted_responses += f"Response {idx+1}:\n"
                        for q_idx, answer in resp.items():
                            formatted_responses += f"Q{q_idx+1}: {answer}\n"
                        formatted_responses += "\n"

                    prompt = f"""
You are SurveyForge — an expert feedback analyst.

Survey: {survey['title']}
Questions: {json.dumps(survey['questions'])}

Responses ({len(responses)} total):
{formatted_responses}

Provide actionable insights:
- Key themes and patterns
- Positive feedback highlights
- Areas for improvement
- Sentiment overview
- Recommendations for the business

Be specific, data-driven, and constructive.
"""

                    response = model.generate_content(prompt)
                    insights = response.text

                    st.success("Insights generated")
                    st.markdown("### AI-Powered Insights")
                    st.markdown(insights)
                except Exception as e:
                    st.error(f"Insights generation failed: {str(e)}")
        else:
            st.info("No responses yet.")

st.markdown("---")
st.caption("SurveyForge • Gather feedback, unlock insights • Powered by Gemini AI")
