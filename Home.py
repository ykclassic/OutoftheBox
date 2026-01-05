import streamlit as st

st.set_page_config(page_title="TechSolute Hub", page_icon="🚀", layout="wide")

# Native CSS to hide footer and the "Deploy" button for a clean look
st.markdown("""
    <style>
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 1. Define your 20 apps
# IMPORTANT: The 4th item must match your filename in the /pages folder exactly (without .py)
apps_data = [
    ["📈", "ForgV1", "Data Analytics and Visualization.", "01_📈_ForgV1"],
    ["🤖", "Forgev2", "AI Content Generator.", "02_🤖_Forgev2"],
    ["🧠", "Forgev3", "Neural Network Model Tester.", "03_🧠_Forgev3"],
    ["⚙️", "Forgev4", "System Utility and Automation.", "04_⚙️_Forgev4"],
    ["📊", "Forgev5", "Market Trend Tracker.", "05_📊_Forgev5"],
    ["🔍", "Forgev6", "SEO Keyword Researcher.", "06_🔍_Forgev6"],
    ["📝", "Forgev7", "Smart Document Summarizer.", "07_📝_Forgev7"],
    ["🖼️", "Forgev8", "Image Processing Suite.", "08_🖼️_Forgev8"],
    ["🔐", "Forgev9", "Encryption & Security Tool.", "09_🔐_Forgev9"],
    ["🌍", "Forgev10", "Language Translator.", "10_🌍_Forgev10"],
    ["📅", "Forgev11", "Project Scheduler.", "11_📅_Forgev11"],
    ["💰", "Forgev12", "Expense & Budget Tracker.", "12_💰_Forgev12"],
    ["🧪", "Forgev13", "Scientific Calculator.", "13_🧪_Forgev13"],
    ["📧", "Forgev14", "Email Marketing Automation.", "14_📧_Forgev14"],
    ["📱", "Forgev15", "Social Media Manager.", "15_📱_Forgev15"],
    ["☁️", "Forgev16", "Cloud Storage Manager.", "16_☁️_Forgev16"],
    ["⚡", "Forgev17", "Fast File Converter.", "17_⚡_Forgev17"],
    ["🎙️", "Forgev18", "Voice-to-Text Studio.", "18_🎙️_Forgev18"],
    ["🎮", "Forgev19", "Game Logic Simulator.", "19_🎮_Forgev19"],
    ["🎨", "Forgev20", "UI/UX Color Palette Generator.", "20_🎨_Forgev20"]
]

# 2. Header Section
st.title("🚀 TechSolute Application Hub")
st.write("Click any card below to launch the specific application.")

# 3. Search Interface
search_query = st.text_input("🔍 Search for an application...", "").lower()
st.write("---")

# 4. Filter logic
filtered_apps = [app for app in apps_data if search_query in app[1].lower() or search_query in app[2].lower()]

# 5. Display Grid (4 columns looks better for 20 apps)
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
                
                # The button that switches the page
                if st.button(f"Launch {name}", key=f"btn_{index}", use_container_width=True):
                    try:
                        st.switch_page(f"pages/{filename}.py")
                    except Exception as e:
                        st.error(f"Could not find {filename}.py in /pages folder")

st.write("---")
st.caption("Developed by TechSolute | 2026 Edition")
