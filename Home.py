import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="TechSolute Hub", page_icon="🚀", layout="wide")

# 2. Native-friendly CSS to hide footer and keep it clean
st.markdown("""
    <style>
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;} /* Hides the extra deploy button */
    </style>
    """, unsafe_allow_html=True)

# 3. App Database (Easily add all 20 apps here)
# Format: ["Icon", "Name", "Description"]
apps = [
    ["📈", "ForgV1", "Data Analytics and Visualization."],
    ["🤖", "Forgev2", "AI Content Generator."],
    ["🧠", "Forgev3", "Neural Network Model Tester."],
    ["⚙️", "Forgev4", "System Utility and Automation."],
    ["📊", "Forgev5", "Market Trend Tracker."],
    ["🔍", "Forgev6", "SEO Keyword Researcher."],
    # ... Just add more rows here until you hit 20
]

# 4. Header Section
st.title("🚀 TechSolute Application Hub")
st.write("Welcome to the central dashboard. Search or browse the apps below.")

# 5. Search Bar
search_query = st.text_input("🔍 Search for an app...", "").lower()

st.write("---")

# 6. Filter and Display Apps in a Grid
# We filter the list based on the search input
filtered_apps = [app for app in apps if search_query in app[1].lower() or search_query in app[2].lower()]

if not filtered_apps:
    st.warning("No apps found matching that search.")
else:
    # This creates a responsive grid (3 columns)
    cols = st.columns(3)
    for index, app in enumerate(filtered_apps):
        icon, name, desc = app
        # This uses the modulo operator to cycle through columns 0, 1, 2
        with cols[index % 3]:
            with st.container(border=True): # Adds a nice box around each app
                st.markdown(f"### {icon} {name}")
                st.write(desc)
                # This hint reminds them to use the sidebar
                st.caption(f"Open '{icon} {name}' in the sidebar ←")

st.write("---")
st.caption("Developed by TechSolute | All rights reserved.")
