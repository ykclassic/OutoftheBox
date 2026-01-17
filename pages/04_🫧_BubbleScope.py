import streamlit as st
import pandas as pd
import plotly.express as px
from google.generativeai import GenerativeModel, configure
from typing import Optional


# --------------------------------------------------
# PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# --------------------------------------------------
st.set_page_config(
    page_title="BubbleScope",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# SECURE GEMINI CONFIGURATION
# --------------------------------------------------
def configure_gemini() -> Optional[GenerativeModel]:
    """
    Safely configure Gemini model.
    Returns model if successful, otherwise None.
    """
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error(
            "Gemini API key not found.\n\n"
            "Add GEMINI_API_KEY to Streamlit secrets."
        )
        return None

    try:
        configure(api_key=api_key)
        return GenerativeModel("gemini-2.5-flash")
    except Exception as exc:
        st.error(f"Failed to initialize Gemini model: {exc}")
        return None


model = configure_gemini()
if model is None:
    st.stop()


# --------------------------------------------------
# UI STYLING (SAFE INLINE CSS)
# --------------------------------------------------
st.markdown(
    """
    <style>
        .title {
            font-size: 48px;
            font-weight: 800;
            text-align: center;
            color: #3498db;
        }
        .subtitle {
            font-size: 22px;
            text-align: center;
            color: #cccccc;
            margin-bottom: 32px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown('<div class="title">BubbleScope</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">'
    "See the shape of your filter bubble and what is hidden beyond it."
    "</div>",
    unsafe_allow_html=True,
)

st.info(
    "Describe your main news sources and topics. "
    "BubbleScope analyzes potential blind spots, hidden viewpoints, "
    "and ways to broaden your information exposure."
)


# --------------------------------------------------
# USER INPUTS
# --------------------------------------------------
sources = st.text_area(
    label="Your main sources and platforms",
    height=100,
    placeholder="Example: Twitter (tech influencers), Reddit (r/technology), NYT",
)

topics = st.text_area(
    label="Topics you follow most",
    height=100,
    placeholder="Example: AI, climate change, US politics, crypto",
)

lean = st.selectbox(
    label="Perceived political or cultural lean (optional)",
    options=[
        "None / Not specified",
        "Left",
        "Center-Left",
        "Center",
        "Center-Right",
        "Right",
    ],
)


# --------------------------------------------------
# PROMPT BUILDER (AST-SAFE)
# --------------------------------------------------
def build_prompt(
    user_sources: str,
    user_topics: str,
    user_lean: str,
) -> str:
    """
    Build Gemini prompt using explicit string concatenation.
    This avoids AST and parsing issues on Streamlit Cloud.
    """
    lean_value = (
        user_lean if user_lean != "None / Not specified" else "Not specified"
    )

    return (
        "You are BubbleScope, an unbiased analyst of information ecosystems.\n\n"
        "User information:\n"
        f"- Sources and platforms: {user_sources}\n"
        f"- Main topics followed: {user_topics}\n"
        f"- Self-described lean: {lean_value}\n\n"
        "Analyze the user's information bubble:\n"
        "1. Which perspectives, stories, or viewpoints are likely hidden or downranked.\n"
        "2. The overall shape of their bubble (ideological skew, topic silos, diversity).\n"
        "3. Five specific examples of content or viewpoints they likely never see.\n"
        "4. Three concrete suggestions (sources or searches) to broaden exposure.\n\n"
        "Be neutral, specific, and constructive. Avoid judgment."
    )


# --------------------------------------------------
# MAIN ACTION
# --------------------------------------------------
if st.button("Scope My Bubble", type="primary"):
    if not sources.strip() and not topics.strip():
        st.warning("Please provide at least sources or topics.")
    else:
        with st.spinner("Mapping your filter bubble..."):
            try:
                prompt = build_prompt(sources, topics, lean)

                response = model.generate_content(prompt)

                analysis_text = getattr(response, "text", "").strip()

                if not analysis_text:
                    st.error("No analysis returned from Gemini.")
                else:
                    st.success("Bubble mapped successfully")
                    st.markdown("### Your Filter Bubble Analysis")
                    st.markdown(analysis_text)

                    # --------------------------------------------------
                    # SIMPLE VISUALIZATION (ILLUSTRATIVE ONLY)
                    # --------------------------------------------------
                    spectrum_data = pd.DataFrame(
                        {
                            "Perspective": [
                                "Far Left",
                                "Left",
                                "Center",
                                "Right",
                                "Far Right",
                            ],
                            "Estimated Exposure (%)": [20, 55, 15, 8, 2],
                        }
                    )

                    fig = px.bar(
                        spectrum_data,
                        x="Perspective",
                        y="Estimated Exposure (%)",
                        title="Estimated Exposure Spectrum (Illustrative)",
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    st.caption(
                        "This visualization is an illustrative estimate based on your inputs, "
                        "not a measured political profile."
                    )

            except Exception as exc:
                st.error(f"Analysis failed: {exc}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption(
    "BubbleScope • See beyond your bubble • Powered by Gemini AI"
)
