import streamlit as st

st.set_page_config(page_title="TechSolute Hub", page_icon="🚀", layout="wide")

# Native CSS to hide footer and clean up the UI
st.markdown("""
    <style>
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 1. Your 20 Custom Apps
# IMPORTANT: Ensure your files in the /pages folder match the 4th column exactly (e.g. 01_🤝_Affili8.py)
apps_data = [
    ["🤝", "Affili8", "Affiliate management and tracking suite.", "01_🤝_Affili8"],
    ["🔥", "AfroForge", "Cultural content generation and design.", "02_🔥_AfroForge"],
    ["🛠️", "AssistForge", "Automated assistant and task helper.", "03_🛠️_AssistForge"],
    ["🫧", "BubbleScope", "Data visualization and trend analysis.", "04_🫧_BubbleScope"],
    ["📊", "ChartExpo", "Advanced charting and presentation engine.", "05_📊_ChartExpo"],
    ["📜", "ClearPact", "Contract simplification and legal clarity.", "06_📜_ClearPact"],
    ["🧠", "ContraMind", "Counter-intuitive logic and brainstorming.", "07_🧠_ContraMind"],
    ["📡", "Echomind", "Feedback loops and mental mapping.", "08_📡_Echomind"],
    ["🚀", "FailForward", "Post-mortem analysis and growth tracking.", "09_🚀_FailForward"],
    ["🎮", "Game", "Interactive logic and simulation module.", "10_🎮_Game"],
    ["👻", "Ghostly", "Anonymous data handling and privacy tools.", "11_👻_Ghostly"],
    ["🎯", "KillShot", "Precision targeting and goal achievement.", "12_🎯_KillShot"],
    ["👤", "Person8", "User persona and demographic profiling.", "13_👤_Person8"],
    ["🔧", "RegretFix", "Error correction and rollback simulation.", "14_🔧_RegretFix"],
    ["🪞", "RetroMirror", "Retrospective analysis and history viewing.", "15_🪞_RetroMirror"],
    ["🛡️", "SkillGuard", "Competency tracking and skill protection.", "16_🛡️_SkillGuard"],
    ["📝", "Summarily", "Rapid text summarization and extraction.", "17_📝_Summarily"],
    ["📋", "Survy", "Dynamic survey generation and response logic.", "18_📋_Survy"],
    ["🌉", "ToneBridge", "Communication style and tone adjustment.", "19_🌉_ToneBridge"],
    ["⚖️", "Verdict", "Decision-making engine and final analysis.", "20_⚖️_Verdict"]
]

# 2. Header Section
st.title("🚀 TechSolute Application Hub")
st.write("Select an application below to launch it instantly.")

# 3. Search Interface
search_query = st.text_input("🔍 Search for a tool...", "").lower()
st.write("---")

# 4. Filter logic
filtered_apps = [app for app in apps_data if search_query in app[1].lower() or search_query in app[2].lower()]

# 5. Display Grid (4 columns)
if not filtered_apps:
    st.warning("No applications match your search.")
else:
    cols = st.columns(4) 
    for index, app in enumerate(filtered_apps):
        icon, name, desc, filename = app
        
        with cols[index % 4]:
            with st.container(border=True):
                st.markdown(f"### {icon} {name}")
                st.write(desc)
                
                # Launch Button
                if st.button(f"Launch {name}", key=f"btn_{index}", use_container_width=True):
                    try:
                        st.switch_page(f"pages/{filename}.py")
                    except Exception:
                        st.error(f"File 'pages/{filename}.py' not found on GitHub.")

st.write("---")
st.caption("Developed by TechSolute | Unified App Environment")
