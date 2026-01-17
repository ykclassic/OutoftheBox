import streamlit as st
import pandas as pd
import plotly.express as px
import random
import time
import uuid
import sqlite3
from datetime import datetime
from google.generativeai import GenerativeModel, configure
import json

# ===============================
# PAGE CONFIG & MOBILE OPTIMIZATION
# ===============================
st.set_page_config(page_title="MindGames", page_icon="🧩", layout="centered")

st.markdown("""
<style>
.block-container { max-width: 720px; padding: 1rem; }
button { width: 100%; height: 3rem; font-size: 1rem; margin-top:0.5rem; }
input, textarea { font-size: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ===============================
# DATABASE LEADERBOARD
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
    c.execute("INSERT INTO leaderboard (username, score, created_at) VALUES (?, ?, ?)",
              (user, score, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def load_leaderboard():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT username, score FROM leaderboard ORDER BY score DESC LIMIT 10", conn)
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
# GEMINI AI SAFE INIT
# ===============================
def init_ai():
    try:
        configure(api_key=st.secrets["GEMINI_API_KEY"])
        return GenerativeModel("gemini-2.5-flash")
    except Exception:
        return None

model = init_ai()
AI_OK = model is not None
if not AI_OK:
    st.warning("AI not available. Using fallback content.")

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
    ],
)

# ===============================
# ROUND RESET HELPER
# ===============================
def reset_round():
    for k in list(st.session_state.keys()):
        if k.startswith("round_"):
            del st.session_state[k]
    st.session_state.step = "start"

# ===============================
# SAFE RIDDLE FALLBACK
# ===============================
def safe_riddle():
    return {
        "riddle": "What has keys but can’t open locks?",
        "answer": "keyboard",
        "reason": "A keyboard has keys used for typing, not unlocking."
    }

# ===============================
# GAME 1: RIDDLE CHALLENGE
# ===============================
if game == "Riddle Challenge":
    st.header("🧠 Riddle Challenge")

    if st.session_state.step == "start":
        if st.button("Generate Riddle"):
            if AI_OK:
                prompt = """
Return ONLY valid JSON:
{"riddle": "...", "answer": "...", "reason": "..."}
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
        st.markdown(f"### {st.session_state.round_riddle}")
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
# GAME 2: CUSTOM QUIZ MASTER
# ===============================
elif game == "Custom Quiz Master":
    st.header("📝 Custom Quiz Master")
    topic = st.text_input("Quiz Topic")

    if st.session_state.step == "start" and st.button("Generate Question"):
        if AI_OK and topic:
            prompt = f"Generate 1 multiple-choice question on {topic} in JSON format: {{'question':'', 'options':['','','',''], 'answer':''}}"
            try:
                raw = model.generate_content(prompt).text
                data = json.loads(raw)
            except Exception:
                data = {
                    "question": f"What is a key concept in {topic}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A"
                }
        else:
            data = {
                "question": f"What is a key concept in {topic or 'this topic'}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A"
            }

        st.session_state.round_question = data
        st.session_state.step = "answer"

    if st.session_state.step == "answer":
        st.markdown(st.session_state.round_question["question"])
        choice = st.radio("Select answer", st.session_state.round_question["options"], key="quiz_choice")
        if st.button("Submit Answer"):
            if choice == st.session_state.round_question["answer"]:
                st.success("Correct! +10 points")
                st.session_state.score += 10
            else:
                st.error("Incorrect ❌")
                st.info(f"Correct Answer: {st.session_state.round_question['answer']}")
            st.session_state.step = "result"

    elif st.session_state.step == "result":
        if st.button("Next Question ▶️"):
            reset_round()

# ===============================
# GAME 3: DATA INSIGHT PUZZLE
# ===============================
elif game == "Data Insight Puzzle":
    st.header("📊 Data Insight Puzzle")
    if st.session_state.step == "start":
        df = pd.DataFrame({
            "Category": ["A","B","C"],
            "Value": [random.randint(10,100) for _ in range(3)]
        })
        st.session_state.round_data = df
        st.session_state.step = "answer"

    if st.session_state.step == "answer":
        st.dataframe(st.session_state.round_data)
        st.text_area("Describe any patterns or insights")
        if st.button("Submit Answer"):
            st.success("+8 points for participation")
            st.session_state.score += 8
            st.session_state.step = "result"

    elif st.session_state.step == "result":
        if st.button("Next Puzzle ▶️"):
            reset_round()

# ===============================
# GAME 4: LOGICAL DEDUCTION
# ===============================
elif game == "Logical Deduction":
    st.header("🧩 Logical Deduction")
    if st.session_state.step == "start":
        st.markdown("If A > B and B > C, is A > C?")
        st.session_state.step = "answer"
    if st.session_state.step == "answer":
        choice = st.radio("Answer", ["Yes", "No"], key="logic_choice")
        if st.button("Submit Answer"):
            if choice == "Yes":
                st.success("Correct! +5 points")
                st.session_state.score += 5
            else:
                st.error("Incorrect ❌")
            st.session_state.step = "result"
    elif st.session_state.step == "result":
        if st.button("Next ▶️"):
            reset_round()

# ===============================
# GAME 5: PATTERN MEMORY
# ===============================
elif game == "Pattern Memory":
    st.header("🔐 Pattern Memory Challenge")
    if st.session_state.step == "start":
        st.session_state.round_pattern = [random.randint(1,9) for _ in range(5)]
        st.session_state.step = "memorize"

    if st.session_state.step == "memorize":
        st.markdown(f"**Memorize this pattern:** `{st.session_state.round_pattern}`")
        time.sleep(2)
        st.session_state.step = "answer"

    if st.session_state.step == "answer":
        guess = st.text_input("Enter pattern (comma separated)")
        if st.button("Submit Pattern"):
            try:
                g = [int(x.strip()) for x in guess.split(",")]
                if g == st.session_state.round_pattern:
                    st.success("Perfect! +15 points")
                    st.session_state.score += 15
                else:
                    st.error("Incorrect ❌")
                st.session_state.step = "result"

    if st.session_state.step == "result":
        if st.button("Next ▶️"):
            reset_round()

# ===============================
# FOOTER & LEADERBOARD
# ===============================
st.markdown("---")
st.markdown(f"### 🏆 Total Score: {st.session_state.score}")

if st.button("Save Score"):
    save_score(st.session_state.username, st.session_state.score)
    st.success("Score saved!")

st.dataframe(load_leaderboard(), use_container_width=True)
