import streamlit as st
import pandas as pd
import plotly.express as px
import random
import time
from google.generativeai import GenerativeModel, configure
from typing import Optional


# ==================================================
# PAGE CONFIG — MOBILE FIRST
# ==================================================
st.set_page_config(
    page_title="MindGames",
    page_icon="🧩",
    layout="centered",
)

# ==================================================
# MOBILE-OPTIMIZED CSS
# ==================================================
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-size: 16px;
    }
    .block-container {
        padding: 1rem;
        max-width: 720px;
    }
    button {
        width: 100%;
        height: 3rem;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    input, textarea {
        font-size: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# GEMINI INIT (VERIFIED)
# ==================================================
def init_gemini() -> Optional[GenerativeModel]:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        configure(api_key=api_key)
        return GenerativeModel("gemini-2.5-flash")
    except Exception:
        return None


model = init_gemini()
if model is None:
    st.error("AI not available.")
    st.stop()

# ==================================================
# GLOBAL STATE
# ==================================================
if "scores" not in st.session_state:
    st.session_state.scores = []

# ==================================================
# HEADER
# ==================================================
st.markdown("## 🧩 MindGames")
st.caption("Short, intelligent games designed for thinking — not guessing.")

# ==================================================
# GAME SELECTOR
# ==================================================
game = st.selectbox(
    "Choose a game",
    [
        "Riddle Challenge",
        "Custom Quiz Master",
        "Data Insight Puzzle",
        "Logical Deduction Grid",
        "Pattern Memory Challenge",
    ],
)

# ==================================================
# GAME 1 — RIDDLE CHALLENGE (UNCHANGED LOGIC)
# ==================================================
if game == "Riddle Challenge":
    if st.button("Generate Riddle"):
        prompt = (
            "Generate a riddle.\n"
            "Format:\n"
            "Riddle: <text>\n"
            "Answer: <answer>"
        )
        r = model.generate_content(prompt).text
        st.session_state.riddle = r.split("Answer:")[0].replace("Riddle:", "").strip()
        st.session_state.answer = r.split("Answer:")[1].strip().lower()

    if "riddle" in st.session_state:
        st.markdown(st.session_state.riddle)
        guess = st.text_input("Your answer")
        if st.button("Submit"):
            if guess.lower().strip() == st.session_state.answer:
                st.success("Correct! +10")
                st.session_state.scores.append(10)
            else:
                st.error("Wrong.")
                st.info(f"Correct answer: {st.session_state.answer}")

# ==================================================
# GAME 2 — QUIZ MASTER (SAFE PARSING)
# ==================================================
elif game == "Custom Quiz Master":
    topic = st.text_input("Quiz topic")
    if st.button("Generate Quiz"):
        prompt = f"Create 3 multiple choice questions on {topic}."
        st.session_state.quiz_text = model.generate_content(prompt).text

    if "quiz_text" in st.session_state:
        st.markdown(st.session_state.quiz_text)
        if st.button("I Read It"):
            st.success("Participation +5")
            st.session_state.scores.append(5)

# ==================================================
# GAME 3 — DATA INSIGHT PUZZLE
# ==================================================
elif game == "Data Insight Puzzle":
    df = pd.DataFrame({
        "Category": ["A", "B", "C", "A", "B", "C"],
        "Value": [random.randint(10, 100) for _ in range(6)],
    })
    st.plotly_chart(px.bar(df, x="Category", y="Value"), use_container_width=True)
    insight = st.text_area("What do you observe?")
    if st.button("Reveal"):
        st.success("AI Insight Revealed +5")
        st.session_state.scores.append(5)

# ==================================================
# GAME 4 — LOGICAL DEDUCTION GRID (NEW)
# ==================================================
elif game == "Logical Deduction Grid":
    st.markdown("### 🧠 Logical Deduction Grid")
    st.info("Three houses: Red, Blue, Green. One has a Cat.")

    clues = [
        "The Red house is not Green.",
        "The Cat is not in Blue.",
        "Green is not next to Red."
    ]

    for c in clues:
        st.markdown(f"- {c}")

    answer = st.selectbox("Where is the Cat?", ["Red", "Blue", "Green"])

    if st.button("Check Answer"):
        if answer == "Red":
            st.success("Correct! +15")
            st.session_state.scores.append(15)
        else:
            st.error("Incorrect. Try again.")

# ==================================================
# GAME 5 — PATTERN MEMORY CHALLENGE (NEW)
# ==================================================
elif game == "Pattern Memory Challenge":
    st.markdown("### 🔐 Pattern Memory Challenge")

    if "pattern" not in st.session_state:
        st.session_state.pattern = [random.randint(1, 9) for _ in range(5)]
        st.session_state.start_time = time.time()

    st.markdown(f"**Memorize this pattern:** `{st.session_state.pattern}`")
    time.sleep(2)
    st.markdown("Pattern hidden. Enter it below.")

    guess = st.text_input("Enter pattern (comma separated)")

    if st.button("Submit Pattern"):
        try:
            g = [int(x.strip()) for x in guess.split(",")]
            if g == st.session_state.pattern:
                st.success("Perfect memory! +20")
                st.session_state.scores.append(20)
            else:
                st.error("Incorrect.")
        except Exception:
            st.error("Invalid input.")

# ==================================================
# SCORE DISPLAY (MOBILE FRIENDLY)
# ==================================================
st.markdown("---")
st.markdown(f"### 🏆 Total Score: {sum(st.session_state.scores)}")
