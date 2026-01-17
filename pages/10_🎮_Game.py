import streamlit as st
import random
import time
import uuid
import sqlite3
import pandas as pd
from datetime import datetime
from google.generativeai import GenerativeModel, configure
import json

# ===============================
# PAGE CONFIG (MOBILE SAFE)
# ===============================
st.set_page_config(
    page_title="MindGames",
    page_icon="🧩",
    layout="centered"
)

st.markdown("""
<style>
.block-container { max-width: 720px; padding: 1rem; }
button { width: 100%; height: 3rem; font-size: 1rem; }
input, textarea { font-size: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ===============================
# DATABASE
# ===============================
DB = "leaderboard.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY,
            username TEXT,
            score INTEGER,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_score(user, score):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO leaderboard (username, score, created_at) VALUES (?, ?, ?)",
        (user, score, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def load_leaderboard():
    conn = sqlite3.connect(DB)
    df = pd.read_sql(
        "SELECT username, score FROM leaderboard ORDER BY score DESC LIMIT 10",
        conn
    )
    conn.close()
    return df

# ===============================
# SESSION STATE
# ===============================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "score" not in st.session_state:
    st.session_state.score = 0

if "step" not in st.session_state:
    st.session_state.step = "start"

if "username" not in st.session_state:
    st.session_state.username = ""

# ===============================
# GEMINI SAFE INIT
# ===============================
def init_ai():
    try:
        configure(api_key=st.secrets["GEMINI_API_KEY"])
        return GenerativeModel("gemini-2.5-flash")
    except Exception:
        return None

model = init_ai()
AI_OK = model is not None

# ===============================
# HEADER
# ===============================
st.markdown("## 🧩 MindGames")
st.caption(f"Session `{st.session_state.session_id[:8]}`")

st.session_state.username = st.text_input("Username", st.session_state.username)

if not st.session_state.username:
    st.warning("Enter a username to play.")
    st.stop()

# ===============================
# GAME SELECT
# ===============================
game = st.selectbox(
    "Choose a game",
    [
        "Riddle Challenge",
        "Custom Quiz Master",
        "Data Insight Puzzle",
        "Logical Deduction",
        "Pattern Memory"
    ]
)

# ===============================
# HELPERS
# ===============================
def reset_round():
    for k in list(st.session_state.keys()):
        if k.startswith("round_"):
            del st.session_state[k]
    st.session_state.step = "start"

def safe_riddle():
    return {
        "riddle": "What has keys but can’t open locks?",
        "answer": "keyboard",
        "reason": "A keyboard has keys used for typing, not unlocking."
    }

# ===============================
# GAME 1 — RIDDLE CHALLENGE
# ===============================
if game == "Riddle Challenge":

    if st.session_state.step == "start":
        if st.button("Generate Riddle"):
            if AI_OK:
                prompt = """
Return ONLY valid JSON in this format:
{
  "riddle": "...",
  "answer": "...",
  "reason": "..."
}
"""
                try:
                    raw = model.generate_content(prompt).text
                    data = json.loads(raw)
                except Exception:
                    data = safe_riddle()
            else:
                data = safe_riddle()

            st.session_state.round_riddle = data["riddle"]
            st.session_state.round_answer = data["answer"].lower().strip()
            st.session_state.round_reason = data["reason"]
            st.session_state.step = "answer"

    elif st.session_state.step == "answer":
        st.markdown(f"### 🧠 Riddle\n{st.session_state.round_riddle}")
        user = st.text_input("Your answer")

        if st.button("Submit Answer"):
            if user.lower().strip() == st.session_state.round_answer:
                st.success("Correct! 🎉 +10 points")
                st.session_state.score += 10
            else:
                st.error("Incorrect ❌")
                st.info(f"**Correct Answer:** {st.session_state.round_answer}")
                st.markdown(f"**Reason:** {st.session_state.round_reason}")

            st.session_state.step = "result"

    elif st.session_state.step == "result":
        if st.button("Next Riddle ▶️"):
            reset_round()

# ===============================
# GAME 2 — QUIZ MASTER
# ===============================
elif game == "Custom Quiz Master":

    if st.session_state.step == "start":
        topic = st.text_input("Quiz Topic")
        if st.button("Generate Question"):
            st.session_state.round_question = f"What is a key concept in {topic}?"
            st.session_state.step = "result"

    elif st.session_state.step == "result":
        st.markdown(st.session_state.round_question)
        st.success("+5 points for participation")
        st.session_state.score += 5

        if st.button("Next ▶️"):
            reset_round()

# ===============================
# GAME 3 — DATA INSIGHT
# ===============================
elif game == "Data Insight Puzzle":

    if st.session_state.step == "start":
        df = pd.DataFrame({
            "Category": ["A", "B", "C"],
            "Value": [random.randint(10, 100) for _ in range(3)]
        })
        st.session_state.round_data = df
        st.session_state.step = "answer"

    elif st.session_state.step == "answer":
        st.dataframe(st.session_state.round_data)
        st.text_area("Describe the pattern")

        if st.button("Submit"):
            st.success("+8 points")
            st.session_state.score += 8
            st.session_state.step = "result"

    elif st.session_state.step == "result":
        if st.button("Next ▶️"):
            reset_round()

# ===============================
# GAME 4 — LOGIC
# ===============================
elif game == "Logical Deduction":
    st.markdown("If A > B and B > C, is A > C?")
    if st.button("Answer"):
        st.success("Correct! +5")
        st.session_state.score += 5

# ===============================
# GAME 5 — MEMORY
# ===============================
elif game == "Pattern Memory":
    if "round_pattern" not in st.session_state:
        st.session_state.round_pattern = [random.randint(1,9) for _ in range(5)]

    st.markdown(f"Memorize: {st.session_state.round_pattern}")
    time.sleep(1)
    guess = st.text_input("Enter pattern")

    if st.button("Check"):
        st.success("+10 points")
        st.session_state.score += 10
        reset_round()

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.markdown(f"### 🏆 Score: {st.session_state.score}")

if st.button("Save Score"):
    save_score(st.session_state.username, st.session_state.score)
    st.success("Saved")

st.dataframe(load_leaderboard(), use_container_width=True)
