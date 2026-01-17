import streamlit as st
import sqlite3
import uuid
import random
import time
import pandas as pd
from datetime import datetime
from google.generativeai import GenerativeModel, configure

# ======================================================
# PAGE CONFIG (MOBILE-FIRST)
# ======================================================
st.set_page_config(page_title="MindGames", page_icon="🧩", layout="centered")

st.markdown("""
<style>
.block-container { max-width: 720px; padding: 1rem; }
button { width: 100%; height: 3rem; font-size: 1rem; }
input, textarea { font-size: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# DATABASE
# ======================================================
DB_PATH = "leaderboard.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score INTEGER,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_score(username, score):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO leaderboard (username, score, created_at) VALUES (?, ?, ?)",
        (username, score, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def load_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT username, score, created_at FROM leaderboard ORDER BY score DESC LIMIT 10",
        conn
    )
    conn.close()
    return df

# ======================================================
# SESSION STATE
# ======================================================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "score" not in st.session_state:
    st.session_state.score = 0

if "username" not in st.session_state:
    st.session_state.username = ""

if "game_step" not in st.session_state:
    st.session_state.game_step = "start"

# ======================================================
# DIFFICULTY ENGINE
# ======================================================
def difficulty(score):
    if score < 30:
        return "Beginner"
    if score < 80:
        return "Intermediate"
    return "Advanced"

# ======================================================
# GEMINI (SAFE INIT)
# ======================================================
def init_gemini():
    try:
        configure(api_key=st.secrets["GEMINI_API_KEY"])
        return GenerativeModel("gemini-2.5-flash")
    except Exception:
        return None

model = init_gemini()
ai_available = model is not None

# ======================================================
# HEADER
# ======================================================
st.markdown("## 🧩 MindGames")
st.caption(
    f"Session `{st.session_state.session_id[:8]}` | "
    f"Difficulty: **{difficulty(st.session_state.score)}**"
)

st.session_state.username = st.text_input(
    "Username", value=st.session_state.username
)

if not st.session_state.username:
    st.warning("Enter a username to play.")
    st.stop()

# ======================================================
# GAME SELECTOR
# ======================================================
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

# ======================================================
# NEXT BUTTON HELPER
# ======================================================
def next_round():
    for key in list(st.session_state.keys()):
        if key.startswith("round_"):
            del st.session_state[key]
    st.session_state.game_step = "start"

# ======================================================
# GAME 1 — RIDDLE CHALLENGE
# ======================================================
if game == "Riddle Challenge":

    if st.session_state.game_step == "start":
        if st.button("Generate Riddle"):
            if ai_available:
                text = model.generate_content(
                    f"Generate a {difficulty(st.session_state.score)} riddle "
                    "with a clear answer and reason."
                ).text
            else:
                text = "Riddle: What has keys but can't open locks?\nAnswer: Keyboard\nReason: It types."

            st.session_state.round_riddle = (
                text.split("Answer:")[0].replace("Riddle:", "").strip()
            )
            rest = text.split("Answer:")[1]
            st.session_state.round_answer = rest.split("Reason:")[0].strip().lower()
            st.session_state.round_reason = rest.split("Reason:")[1].strip()
            st.session_state.game_step = "answer"

    elif st.session_state.game_step == "answer":
        st.markdown(st.session_state.round_riddle)
        user = st.text_input("Your answer", key="riddle_input")

        if st.button("Submit"):
            if user.lower().strip() == st.session_state.round_answer:
                st.success("Correct! +10")
                st.session_state.score += 10
            else:
                st.error("Wrong")
                st.info(f"Answer: {st.session_state.round_answer}")
                st.markdown(st.session_state.round_reason)

            st.session_state.game_step = "result"

    elif st.session_state.game_step == "result":
        if st.button("Next Riddle ▶️"):
            next_round()

# ======================================================
# GAME 2 — QUIZ MASTER
# ======================================================
elif game == "Custom Quiz Master":

    if st.session_state.game_step == "start":
        topic = st.text_input("Quiz topic", key="quiz_topic")

        if st.button("Generate Question"):
            if ai_available:
                st.session_state.round_quiz = model.generate_content(
                    f"One {difficulty(st.session_state.score)} multiple-choice question "
                    f"on {topic} with correct answer."
                ).text
            else:
                st.session_state.round_quiz = (
                    "Question: 2 + 2?\nA)3 B)4 C)5\nAnswer: B"
                )
            st.session_state.game_step = "result"

    elif st.session_state.game_step == "result":
        st.markdown(st.session_state.round_quiz)
        st.success("+5 points for participation")
        st.session_state.score += 5

        if st.button("Next Quiz ▶️"):
            next_round()

# ======================================================
# GAME 3 — DATA INSIGHT PUZZLE
# ======================================================
elif game == "Data Insight Puzzle":

    if st.session_state.game_step == "start":
        df = pd.DataFrame({
            "Category": ["A", "B", "C", "A", "B", "C"],
            "Value": [random.randint(10, 100) for _ in range(6)]
        })
        st.session_state.round_data = df
        st.session_state.game_step = "answer"

    elif st.session_state.game_step == "answer":
        st.dataframe(st.session_state.round_data)
        insight = st.text_area("Describe the pattern")

        if st.button("Evaluate"):
            keywords = {"trend", "increase", "decrease", "variation", "category"}
            user_words = set(insight.lower().split())
            score = int(
                len(keywords & user_words) / len(keywords | user_words) * 20
            )
            st.success(f"+{score} points")
            st.session_state.score += score
            st.session_state.game_step = "result"

    elif st.session_state.game_step == "result":
        if st.button("Next Dataset ▶️"):
            next_round()

# ======================================================
# GAME 4 — LOGICAL DEDUCTION
# ======================================================
elif game == "Logical Deduction Grid":

    st.markdown("Three houses: Red, Blue, Green.")
    st.markdown("- Cat is not in Blue")
    st.markdown("- Green is not next to Red")

    guess = st.selectbox("Where is the Cat?", ["Red", "Blue", "Green"])

    if st.button("Check"):
        if guess == "Red":
            st.success("+15 points")
            st.session_state.score += 15
        else:
            st.error("Incorrect")

        if st.button("Next Puzzle ▶️"):
            next_round()

# ======================================================
# GAME 5 — PATTERN MEMORY
# ======================================================
elif game == "Pattern Memory Challenge":

    if "round_pattern" not in st.session_state:
        length = 5 if difficulty(st.session_state.score) == "Beginner" else 7
        st.session_state.round_pattern = [
            random.randint(1, 9) for _ in range(length)
        ]

    st.markdown(f"Memorize: `{st.session_state.round_pattern}`")
    time.sleep(2)
    st.markdown("Pattern hidden")

    guess = st.text_input("Enter numbers separated by commas")

    if st.button("Submit"):
        try:
            if [int(x.strip()) for x in guess.split(",")] == st.session_state.round_pattern:
                st.success("+20 points")
                st.session_state.score += 20
            else:
                st.error("Incorrect pattern")
        except Exception:
            st.error("Invalid input")

        if st.button("Next Pattern ▶️"):
            next_round()

# ======================================================
# SCORE + LEADERBOARD
# ======================================================
st.markdown("---")
st.markdown(f"### 🏆 Score: {st.session_state.score}")

if st.button("Save Score"):
    save_score(st.session_state.username, st.session_state.score)
    st.success("Score saved")

st.markdown("### 🌍 Leaderboard")
st.dataframe(load_leaderboard(), use_container_width=True)
