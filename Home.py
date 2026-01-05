import streamlit as st

st.set_page_config(page_title="TechSolute Hub", page_icon="🚀", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* Styles the social media footer in the sidebar */
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        width: 15%;
        font-size: 14px;
        color: #888;
        background-color: transparent;
    }
    .sidebar-footer a {
        text-decoration: none;
        color: #4F8BF9;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. SESSION STATE FOR FAVORITES ---
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# --- 2. APP DATA (Filenames matched to your Emoji Rename List) ---
apps_data = [
    ["🤝", "Affili8", "Affiliate management suite.", "01_🤝_Affili8"],
    ["🔥", "AfroForge", "Cultural content generation.", "02_🔥_AfroForge"],
    ["🛠️", "AssistForge", "Automated task helper.", "03_🛠️_AssistForge"],
    ["🫧", "BubbleScope", "Data trend analysis.", "04_🫧_BubbleScope"],
    ["📊", "ChartExpo", "Advanced charting engine.", "05_📊_ChartExpo"],
    ["📜", "ClearPact", "Legal clarity tools.", "06_📜_ClearPact"],
    ["🧠", "ContraMind", "Counter-intuitive logic.", "07_🧠_ContraMind"],
    ["📡", "Echomind", "Feedback loops.", "08_📡_Echomind"],
    ["🚀", "FailForward", "Growth tracking.", "09_🚀_FailForward"],
    ["🎮", "Game", "Interactive logic.", "10_🎮_Game"],
    ["👻", "Ghostly", "Privacy tools.", "11_👻_Ghostly"],
    ["🎯", "KillShot", "Precision targeting.", "12_🎯_KillShot"],
    ["👤", "Person8", "User profiling.", "13_👤_Person8"],
    ["🔧", "RegretFix", "Error correction.", "14_🔧_RegretFix"],
    ["🪞", "RetroMirror", "History analysis.", "15_🪞_RetroMirror"],
    ["🛡️", "SkillGuard", "Competency tracking.", "16_🛡️_SkillGuard"],
    ["📝", "Summarily", "Rapid summarization.", "17_📝_Summarily"],
    ["📋", "Survy", "Dynamic surveys.", "18_📋_Survy"],
    ["🌉", "ToneBridge", "Communication style.", "19_🌉_ToneBridge"],
    ["⚖️", "Verdict", "Decision engine.", "20_⚖️_Verdict"]
]

# --- 3. SIDEBAR WITH SOCIALS ---
with st.sidebar:
    st.title("Navigation")
    st.write("---")
    
    # Space for natural Streamlit sidebar navigation will appear here
    
    st.markdown(f"""
        <div class="sidebar-footer">
            <b>Connect with us:</b><br>
            🐦 <a href="https://twitter.com/YourHandle" target="_blank">Twitter</a><br>
            📸 <a href="https://instagram.com/YourHandle" target="_blank">Instagram</a><br>
            💼 <a href="https://linkedin.com/in/YourHandle" target="_blank">LinkedIn</a><br>
            <br>
            <span>© 2026 TechSolute</span>
        </div>
    """, unsafe_allow_html=True)

# --- 4. MAIN DASHBOARD ---
st.title("🚀 TechSolute Application Hub")

# Favorites Section
if st.session_state.favorites:
    st.subheader("⭐ Your Favorites")
    fav_cols = st.columns(4)
    fav_apps = [a for a in apps_data if a[1] in st.session_state.favorites]
    for i, app in enumerate(fav_apps):
        with fav_cols[i % 4]:
            with st.container(border=True):
                st.markdown(f"#### {app[0]} {app[1]}")
                if st.button(f"Launch", key=f"fav_{app[1]}", use_container_width=True):
                    st.switch_page(f"pages/{app[3]}.py")
                if st.button(f"💔 Remove", key=f"unfav_{app[1]}", use_container_width=True):
                    st.session_state.favorites.remove(app[1])
                    st.rerun()
    st.write("---")

# Search and All Apps Grid
st.subheader("🛠️ All Applications")
search_query = st.text_input("🔍 Search for a tool...", "").lower()
filtered_apps = [app for app in apps_data if search_query in app[1].lower()]

if not filtered_apps:
    st.warning("No applications found.")
else:
    cols = st.columns(4) 
    for index, app in enumerate(filtered_apps):
        icon, name, desc, filename = app
        with cols[index % 4]:
            with st.container(border=True):
                st.markdown(f"### {icon} {name}")
                st.write(desc)
                
                # Layout for Launch and Star button
                btn_col, star_col = st.columns([3, 1])
                with btn_col:
                    if st.button(f"Launch", key=f"btn_{index}", use_container_width=True):
                        st.switch_page(f"pages/{filename}.py")
                with star_col:
                    if name not in st.session_state.favorites:
                        if st.button("⭐", key=f"star_{index}", use_container_width=True):
                            st.session_state.favorites.append(name)
                            st.rerun()

st.write("---")
st.caption("Developed by TechSolute | Unified App Environment")
