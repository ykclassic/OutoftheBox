import streamlit as st
import pandas as pd
import plotly.express as px
import random
from google.generativeai import GenerativeModel, configure
from typing import Optional


# ==================================================
# PAGE CONFIG — MUST BE FIRST STREAMLIT CALL
# ==================================================
st.set_page_config(
    page_title="MindGames",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# HIDE STREAMLIT UI
# ==================================================
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# GEMINI CONFIGURATION (SAFE)
# ==================================================
def init_gemini() -> Optional[GenerativeModel]:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("GEMINI_API_KEY missing in Streamlit secrets.")
        return None

    try:
        configure(api_key=api_key)
        return GenerativeModel("gemini-2.5-flash")
    except Exception as exc:
        st.error(f"Failed to initialize Gemini: {exc}")
        return None


model = init_gemini()
if model is None:
    st.stop()

# ==================================================
# STYLING
# ==================================================
st.markdown(
    """
    <style>
        .title { font-size: 48px; font-weight: 800; text-align: center; color: #9b59b6; }
        .subtitle { font-size: 22px; text-align: center; color: #cccccc; margin-bottom: 32px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">🧩 MindGames</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Fun and intellectual games powered by AI, data, and visuals.</div>',
    unsafe_allow_html=True,
)

# ==================================================
# GLOBAL STATE
# ==================================================
if "scores" not in st.session_state:
    st.session_state.scores = []

# ==================================================
# GAME SELECTOR
# ==================================================
game = st.selectbox(
    "Choose a Game",
    ["Riddle Challenge", "Custom Quiz Master", "Data Insight Puzzle"],
)

# ==================================================
# GAME 1 — RIDDLE CHALLENGE (KEPT & FIXED)
# ==================================================
if game == "Riddle Challenge":
    st.header("🧠 Riddle Challenge")
    st.info("Solve the AI-generated riddle. Correct answers earn points.")

    if "riddle_active" not in st.session_state:
        st.session_state.riddle_active = False

    if st.button("Generate New Riddle"):
        prompt = (
            "Generate a clever riddle.\n"
            "Format exactly:\n"
            "Riddle: <text>\n"
            "Answer: <answer>\n"
            "Reason: <short explanation>"
        )
        response = model.generate_content(prompt)
        text = getattr(response, "text", "").strip()

        if "Riddle:" in text and "Answer:" in text and "Reason:" in text:
            st.session_state.riddle = text.split("Answer:")[0].replace("Riddle:", "").strip()
            st.session_state.answer = text.split("Answer:")[1].split("Reason:")[0].strip().lower()
            st.session_state.reason = text.split("Reason:")[1].strip()
            st.session_state.riddle_active = True
            st.session_state.riddle_answered = False
        else:
            st.error("AI returned invalid riddle format.")

    if st.session_state.get("riddle_active"):
        st.markdown(f"### 🧩 {st.session_state.riddle}")
        user_answer = st.text_input("Your answer", key="riddle_input")

        if st.button("Submit Answer") and not st.session_state.riddle_answered:
            st.session_state.riddle_answered = True
            if user_answer.strip().lower() == st.session_state.answer:
                st.success("Correct! 🎉 +10 points")
                st.session_state.scores.append(10)
            else:
                st.error("Wrong answer ❌")
                st.markdown(
                    f"**Correct answer:** {st.session_state.answer}\n\n"
                    f"**Reason:** {st.session_state.reason}"
                )
                st.session_state.scores.append(0)

# ==================================================
# GAME 2 — CUSTOM QUIZ MASTER (FULL REWRITE)
# ==================================================
elif game == "Custom Quiz Master":
    st.header("📝 Custom Quiz Master")
    st.info("AI creates a quiz. Answer once for a final score.")

    topic = st.text_input("Quiz topic")
    num_q = st.slider("Number of questions", 3, 8, 5)

    if st.button("Generate Quiz"):
        prompt = (
            f"Create a {num_q}-question multiple-choice quiz on {topic}.\n"
            "Each question format:\n"
            "Question: <text>\n"
            "A) <option>\n"
            "B) <option>\n"
            "C) <option>\n"
            "D) <option>\n"
            "Correct: <letter>"
        )

        response = model.generate_content(prompt)
        lines = getattr(response, "text", "").splitlines()

        questions = []
        current = {}

        for line in lines:
            line = line.strip()
            if line.startswith("Question:"):
                if current:
                    questions.append(current)
                current = {"q": line, "opts": [], "ans": ""}
            elif line.startswith(("A)", "B)", "C)", "D)")):
                current["opts"].append(line)
            elif line.startswith("Correct:"):
                current["ans"] = line.replace("Correct:", "").strip()

        if current:
            questions.append(current)

        if not questions:
            st.error("Quiz generation failed.")
        else:
            st.session_state.quiz = questions
            st.session_state.quiz_done = False

    if "quiz" in st.session_state:
        answers = []
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"**{q['q']}**")
            ans = st.radio("Choose", q["opts"], key=f"quiz_{i}", label_visibility="collapsed")
            answers.append(ans)

        if st.button("Submit Quiz") and not st.session_state.quiz_done:
            score = 0
            for i, q in enumerate(st.session_state.quiz):
                if answers[i] and q["ans"] in answers[i]:
                    score += 1

            st.session_state.quiz_done = True
            st.success(f"You scored {score}/{len(st.session_state.quiz)}")
            st.session_state.scores.append(score * 2)

# ==================================================
# GAME 3 — DATA INSIGHT PUZZLE (FULL REWRITE)
# ==================================================
elif game == "Data Insight Puzzle":
    st.header("📊 Data Insight Puzzle")
    st.info("Interpret a dataset and compare your insight with the AI.")

    if st.button("Generate Dataset"):
        cats = random.choice(
            [["Red", "Blue", "Green"], ["Q1", "Q2", "Q3"], ["Apple", "Banana", "Orange"]]
        )
        df = pd.DataFrame(
            {"Category": cats * 5, "Value": random.sample(range(10, 100), 15)}
        )
        st.session_state.dataset = df
        st.session_state.data_done = False

    if "dataset" in st.session_state:
        st.plotly_chart(
            px.bar(st.session_state.dataset, x="Category", y="Value"),
            use_container_width=True,
        )

        user_guess = st.text_area("What pattern or story do you see?")

        if st.button("Reveal AI Insight") and not st.session_state.data_done:
            csv_data = st.session_state.dataset.to_csv(index=False)
            prompt = (
                "Analyze this dataset and describe the main pattern or insight.\n\n"
                f"{csv_data}"
            )
            response = model.generate_content(prompt)
            insight = getattr(response, "text", "").strip()

            st.markdown("### AI Insight")
            st.markdown(insight)

            st.success("Insight revealed. +5 participation points")
            st.session_state.scores.append(5)
            st.session_state.data_done = True

# ==================================================
# SCOREBOARD
# ==================================================
if st.session_state.scores:
    total = sum(st.session_state.scores)
    st.sidebar.markdown(f"### 🏆 Total Score: {total}")
    df = pd.DataFrame(
        {"Session": range(1, len(st.session_state.scores) + 1), "Points": st.session_state.scores}
    )
    st.sidebar.plotly_chart(
        px.line(df, x="Session", y="Points", title="Progress"),
        use_container_width=True,
    )

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.caption("MindGames • Fun and intellectual challenges • Powered by Gemini AI")
