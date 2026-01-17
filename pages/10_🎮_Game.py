import streamlit as st
import pandas as pd
import plotly.express as px
import uuid
from datetime import datetime
from google.generativeai import GenerativeModel, configure
import json
import time

# ===============================
# PAGE CONFIG & MOBILE OPTIMIZATION
# ===============================
st.set_page_config(page_title="MindGames AI", page_icon="🧩", layout="centered")
st.markdown("""
<style>
.block-container { max-width: 720px; padding: 1rem; }
button { width: 100%; height: 3rem; font-size: 1rem; margin-top:0.5rem; }
input, textarea { font-size: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ===============================
# GEMINI AI CONFIG
# ===============================
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel("gemini-2.5-flash")

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

st.session_state.username = st.text_input("Enter your username", st.session_state.username)
if not st.session_state.username:
    st.warning("Enter a username to start playing.")
    st.stop()

st.markdown("## 🧩 MindGames AI")
st.caption(f"Session `{st.session_state.session_id[:8]}`")

# ===============================
# GAME SELECTION
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
# ROUND RESET
# ===============================
def reset_round():
    for k in list(st.session_state.keys()):
        if k.startswith("round_"):
            del st.session_state[k]
    st.session_state.step = "start"

# ===============================
# AI HELPER
# ===============================
def generate_ai(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"AI generation failed: {str(e)}")
        return None

def parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        return None

# ===============================
# GAME 1: RIDDLE CHALLENGE
# ===============================
if game == "Riddle Challenge":
    st.header("🧠 Riddle Challenge")
    
    if st.session_state.step == "start":
        if st.button("Generate Riddle"):
            prompt = """
Return ONLY valid JSON:
{"riddle":"...", "answer":"...", "reason":"..."}
Make it fun and intellectual.
"""
            data = parse_json(generate_ai(prompt))
            if data:
                st.session_state.round_riddle = data
                st.session_state.step = "answer"

    if st.session_state.step == "answer":
        st.markdown(f"### {st.session_state.round_riddle['riddle']}")
        user_answer = st.text_input("Your answer")
        if st.button("Submit Answer"):
            if user_answer.lower().strip() == st.session_state.round_riddle["answer"].lower().strip():
                st.success("Correct! 🎉")
                st.session_state.score += 10
            else:
                st.error("Incorrect ❌")
                st.info(f"**Correct Answer:** {st.session_state.round_riddle['answer']}")
                st.markdown(f"**Reason:** {st.session_state.round_riddle['reason']}")
            st.session_state.step = "result"

    if st.session_state.step == "result":
        if st.button("Next ▶️"):
            reset_round()

# ===============================
# GAME 2: CUSTOM QUIZ MASTER
# ===============================
elif game == "Custom Quiz Master":
    st.header("📝 Custom Quiz Master")
    topic = st.text_input("Quiz Topic")

    if st.session_state.step == "start":
        if st.button("Generate Question"):
            prompt = f"""
Return ONLY valid JSON:
{{"question":"...","options":["...","...","...","..."],"answer":"..."}}
Generate a single multiple-choice question on the topic: {topic}.
"""
            data = parse_json(generate_ai(prompt))
            if data:
                st.session_state.round_question = data
                st.session_state.step = "answer"

    if st.session_state.step == "answer":
        st.markdown(st.session_state.round_question["question"])
        choice = st.radio("Select answer", st.session_state.round_question["options"], key="quiz_choice")
        if st.button("Submit Answer"):
            if choice == st.session_state.round_question["answer"]:
                st.success("Correct! 🎉")
                st.session_state.score += 10
            else:
                st.error("Incorrect ❌")
                st.info(f"**Correct Answer:** {st.session_state.round_question['answer']}")
            st.session_state.step = "result"

    if st.session_state.step == "result":
        if st.button("Next ▶️"):
            reset_round()

# ===============================
# GAME 3: DATA INSIGHT PUZZLE
# ===============================
elif game == "Data Insight Puzzle":
    st.header("📊 Data Insight Puzzle")
    
    if st.session_state.step == "start":
        prompt = """
Return ONLY valid JSON:
{"data":[{"Category":"A","Value":..},{"Category":"B","Value":..},{"Category":"C","Value":..}]}
Generate a small random dataset with 3-5 rows and integer values.
"""
        data = parse_json(generate_ai(prompt))
        if data:
            df = pd.DataFrame(data["data"])
            st.session_state.round_data = df
            st.session_state.step = "answer"

    if st.session_state.step == "answer":
        st.dataframe(st.session_state.round_data)
        guess = st.text_input("Describe the hidden pattern or story in the data")
        if st.button("Submit Answer"):
            # AI can score or comment on guess dynamically
            prompt = f"""
Evaluate the user's guess: "{guess}" for the dataset: {st.session_state.round_data.to_dict(orient='records')}
Return JSON: {{"score":int,"feedback":"..."}}.
"""
            result = parse_json(generate_ai(prompt))
            if result:
                st.info(f"AI Feedback: {result['feedback']}")
                st.success(f"Points Earned: {result['score']}")
                st.session_state.score += result["score"]
            st.session_state.step = "result"

    if st.session_state.step == "result":
        if st.button("Next ▶️"):
            reset_round()

# ===============================
# GAME 4: LOGICAL DEDUCTION
# ===============================
elif game == "Logical Deduction":
    st.header("🧩 Logical Deduction")
    
    if st.session_state.step == "start":
        prompt = """
Return ONLY valid JSON:
{"problem":"...", "options":["Yes","No"], "answer":"...","explanation":"..."}
Generate a reasoning/logical puzzle.
"""
        data = parse_json(generate_ai(prompt))
        if data:
            st.session_state.round_logic = data
            st.session_state.step = "answer"

    if st.session_state.step == "answer":
        st.markdown(st.session_state.round_logic["problem"])
        choice = st.radio("Answer", st.session_state.round_logic["options"], key="logic_choice")
        if st.button("Submit Answer"):
            if choice == st.session_state.round_logic["answer"]:
                st.success("Correct! 🎉")
                st.session_state.score += 10
            else:
                st.error("Incorrect ❌")
                st.info(f"Correct Answer: {st.session_state.round_logic['answer']}")
                st.markdown(f"Explanation: {st.session_state.round_logic['explanation']}")
            st.session_state.step = "result"

    if st.session_state.step == "result":
        if st.button("Next ▶️"):
            reset_round()

# ===============================
# GAME 5: PATTERN MEMORY
# ===============================
elif game == "Pattern Memory":
    st.header("🔐 Pattern Memory Challenge")
    
    if st.session_state.step == "start":
        prompt = """
Return ONLY valid JSON:
{"pattern":[.., .., .., .., ..]}
Generate a random 5-number sequence for memory challenge.
"""
        data = parse_json(generate_ai(prompt))
        if data:
            st.session_state.round_pattern = data["pattern"]
            st.session_state.step = "memorize"

    if st.session_state.step == "memorize":
        st.markdown(f"**Memorize this pattern:** {st.session_state.round_pattern}")
        time.sleep(3)
        st.session_state.step = "answer"

    if st.session_state.step == "answer":
        guess = st.text_input("Enter the pattern (comma-separated)")
        if st.button("Submit Pattern"):
            try:
                user_pattern = [int(x.strip()) for x in guess.split(",")]
                prompt = f"""
User entered: {user_pattern}
Original pattern: {st.session_state.round_pattern}
Return JSON: {{"score":int,"feedback":"..."}} evaluating correctness.
"""
                result = parse_json(generate_ai(prompt))
                if result:
                    st.info(f"AI Feedback: {result['feedback']}")
                    st.success(f"Points Earned: {result['score']}")
                    st.session_state.score += result["score"]
            except Exception:
                st.error("Invalid input format. Use comma-separated numbers.")
            st.session_state.step = "result"

    if st.session_state.step == "result":
        if st.button("Next ▶️"):
            reset_round()

# ===============================
# FOOTER: SCOREBOARD
# ===============================
st.markdown("---")
st.markdown(f"### Total Score: {st.session_state.score}")
