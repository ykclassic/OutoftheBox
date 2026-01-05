import streamlit as st

# MUST be the first streamlit command
st.set_page_config(
    page_title="My App Hub",
    page_icon="🚀",
    layout="wide"
)

# --- MAIN CONTENT ---
st.title("Welcome to My Tool Suite. This is a collection of various tool for different purposes")
st.write("---")

st.markdown("""
### 🛠 Available Applications
Choose a tool from the sidebar to begin. Here is a quick overview of what you'll find:
""")

# Creating a 3-column layout for a dashboard feel
col1, col2, col3 = st.columns(3)

with col1:
    st.info("#### 📈 App One")
    st.write("Description of your first app. Great for data analysis or specific tasks.")

with col2:
    st.success("#### 🤖 App Two")
    st.write("Description of your second app. Powered by OpenAI/LLMs.")

with col3:
    st.warning("#### ⚙️ App Three")
    st.write("Description of your third app. Utility tools and settings.")

st.write("---")
st.caption("Developed by [Your Name] | All apps share a secure API environment.")
