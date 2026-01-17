import streamlit as st

# 1. Hide the standard menu and footer using CSS
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
from google.generativeai import GenerativeModel, configure
import pandas as pd
import plotly.express as px
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import random

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="MindGames", page_icon="🧩", layout="wide")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#9b59b6; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🧩 MindGames</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Fun and intellectual games powered by AI, data, and visuals.</p>', unsafe_allow_html=True)

game = st.selectbox("Choose a Game", [
    "Riddle Challenge",
    "Custom Quiz Master",
    "Data Insight Puzzle"
])

if 'scores' not in st.session_state:
    st.session_state.scores = []

# ------------------------------
# Game 1: Riddle Challenge (FIXED)
# ------------------------------
if game == "Riddle Challenge":
    st.header("🧠 Riddle Challenge")
    st.info("AI generates a riddle. Solve it for points!")

    # Initialize state safely
    if "current_riddle" not in st.session_state:
        st.session_state.current_riddle = None
        st.session_state.current_answer = None
        st.session_state.current_reason = None
        st.session_state.answered = False

    # Generate riddle
    if st.button("Generate New Riddle"):
        with st.spinner("Crafting a clever riddle..."):
            prompt = (
                "Generate a fun, intellectual riddle with a clear answer and a short reason.\n"
                "Format exactly as:\n"
                "Riddle: <riddle>\n"
                "Answer: <answer>\n"
                "Reason: <reason>"
            )
            response = model.generate_content(prompt)
            text = getattr(response, "text", "").strip()

            if "Riddle:" in text and "Answer:" in text and "Reason:" in text:
                riddle_part = text.split("Answer:")[0].replace("Riddle:", "").strip()
                answer_part = text.split("Answer:")[1].split("Reason:")[0].strip()
                reason_part = text.split("Reason:")[1].strip()

                st.session_state.current_riddle = riddle_part
                st.session_state.current_answer = answer_part.lower()
                st.session_state.current_reason = reason_part
                st.session_state.answered = False
            else:
                st.error("AI response was not in the expected format.")

    # Display riddle if available
    if st.session_state.current_riddle:
        st.markdown(f"### 🧩 {st.session_state.current_riddle}")

        user_answer = st.text_input("Your answer", key="riddle_answer")

        if st.button("Submit Answer") and not st.session_state.answered:
            st.session_state.answered = True

            if user_answer.strip().lower() == st.session_state.current_answer:
                st.success("Correct! 🎉 +10 points")
                st.session_state.scores.append(10)
            else:
                st.error("Wrong answer ❌")
                st.markdown(
                    f"**Correct answer:** {st.session_state.current_answer}\n\n"
                    f"**Reason:** {st.session_state.current_reason}"
                )
                st.session_state.scores.append(0)


# Game 2: Custom Quiz Master
elif game == "Custom Quiz Master":
    st.header("📝 Custom Quiz Master")
    st.info("AI creates a quiz on your topic. Test your knowledge!")

    topic = st.text_input("Quiz Topic", placeholder="e.g., Python programming, Ancient History, Machine Learning")
    num_questions = st.slider("Number of Questions", 3, 10, 5)

    if st.button("Generate Quiz"):
        if topic:
            with st.spinner("Creating your custom quiz..."):
                prompt = f"""
Create a {num_questions}-question multiple-choice quiz on {topic}.
Format each question as:
Q{{n}}: [question]
A) [option1]
B) [option2]
C) [option3]
D) [option4]

Correct answer: [letter]

Make questions intellectual and fun.
"""

                response = model.generate_content(prompt)
                quiz_text = response.text

                # Parse quiz
                questions = []
                lines = quiz_text.split('\n')
                current_q = {}
                for line in lines:
                    if line.startswith("Q"):
                        if current_q:
                            questions.append(current_q)
                        current_q = {"question": line, "options": [], "answer": ""}
                    elif line.startswith(("A)", "B)", "C)", "D)")):
                        current_q["options"].append(line)
                    elif line.startswith("Correct answer:"):
                        current_q["answer"] = line.split(":")[1].strip()

                if current_q:
                    questions.append(current_q)

                st.session_state.quiz_questions = questions
                st.session_state.user_answers = [None] * len(questions)
                st.session_state.quiz_score = 0

            st.markdown("### Your Quiz")
            for idx, q in enumerate(questions):
                st.markdown(f"**{q['question']}**")
                answer = st.radio("Choose", q['options'], key=f"q{idx}", label_visibility="collapsed")
                st.session_state.user_answers[idx] = answer

            if st.button("Submit Quiz"):
                score = 0
                for idx, q in enumerate(questions):
                    if st.session_state.user_answers[idx] and q['answer'] in st.session_state.user_answers[idx]:
                        score += 1

                st.success(f"You scored {score}/{len(questions)}!")
                st.session_state.scores.append(score * 2)  # 2 points per correct

# Game 3: Data Insight Puzzle
elif game == "Data Insight Puzzle":
    st.header("📈 Data Insight Puzzle")
    st.info("AI generates random data. Guess the hidden story or pattern!")

    if st.button("Generate New Dataset"):
        # Generate random data with pandas
        categories = random.choice([["Red", "Blue", "Green", "Yellow"], ["Apple", "Banana", "Orange", "Grape"], ["Q1", "Q2", "Q3", "Q4"]])
        df = pd.DataFrame({
            "Category": categories * 5,
            "Value": random.sample(range(10, 100), 20)
        })

        st.session_state.current_data = df

        fig = px.bar(df, x="Category", y="Value", title="Mystery Dataset")
        st.plotly_chart(fig, use_container_width=True)

        st.session_state.data_story = None

    if 'current_data' in st.session_state:
        guess = st.text_area("What story or pattern do you see in this data?")
        
        if st.button("Reveal AI Insight"):
            with st.spinner("Analyzing the data..."):
                data_str = st.session_state.current_data.to_csv(index=False)
                
                prompt = f"""
You are a data detective.

Dataset:
{data_str}

What hidden story, pattern, or insight is in this data?
Be intellectual and fun — explain like telling a story.
"""

                response = model.generate_content(prompt)
                insight = response.text

                st.markdown("### AI Data Insight")
                st.markdown(insight)

                # Simple scoring (fun)
                st.session_state.scores.append(5)  # Participation points

# Scoreboard
if st.session_state.scores:
    total = sum(st.session_state.scores)
    st.sidebar.markdown(f"### Total Score: {total} points")
    score_df = pd.DataFrame({"Game Session": range(1, len(st.session_state.scores)+1), "Points": st.session_state.scores})
    fig = px.line(score_df, x="Game Session", y="Points", title="Your Progress")
    st.sidebar.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("MindGames • Fun and intellectual challenges • Powered by Gemini AI")
