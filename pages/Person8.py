import streamlit as st
from google.generativeai import GenerativeModel, configure
import replicate
from fpdf2 import FPDF
import base64
import requests
from io import BytesIO

# Secure API keys
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

try:
    replicate_client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
except KeyError:
    st.error("Replicate API token not found. Add REPLICATE_API_TOKEN to Streamlit secrets.")
    st.stop()

gemini_model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="PersonalForge", page_icon="✨", layout="wide")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#9b59b6; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">✨ PersonalForge</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">AI-generated personalized digital products — just for you.</p>', unsafe_allow_html=True)

st.info("Choose a product, add your details, and PersonalForge creates something uniquely yours.")

product = st.selectbox("Product Type", ["Custom Wallpaper", "Personalized Planner", "Short Custom Ebook"])

name = st.text_input("Your name (optional)")
interests = st.text_area("Your interests, goals, or vibe (e.g., 'motivation, nature, minimalism')", height=100)

if st.button("Forge My Product", type="primary"):
    if not interests.strip():
        st.warning("Share your interests for better personalization.")
    else:
        with st.spinner("Forging your personal product..."):
            try:
                if product == "Custom Wallpaper":
                    prompt = f"High-resolution phone wallpaper: {interests}. Personal touch for {name or 'someone special'}. Beautiful, aesthetic, vibrant colors, no text."

                    outputs = replicate_client.run(
                        "black-forest-labs/flux-dev",
                        input={
                            "prompt": prompt,
                            "num_outputs": 1,
                            "aspect_ratio": "9:16"  # Phone vertical
                        }
                    )

                    img_url = outputs[0]
                    response = requests.get(img_url)
                    img = Image.open(BytesIO(response.content))

                    st.success("Wallpaper forged!")
                    st.image(img, caption="Your Personal Wallpaper", use_column_width=True)

                    st.download_button(
                        "📱 Download Wallpaper",
                        data=response.content,
                        file_name="personalforge_wallpaper.png",
                        mime="image/png"
                    )

                elif product == "Personalized Planner":
                    prompt = f"""
Create a simple 7-day personal planner for {name or 'me'} with interests in {interests}.

Include:
- Daily motivation quote
- Goal section
- To-do list
- Gratitude spot
- Evening reflection

Make it encouraging and tailored.
"""

                    response = gemini_model.generate_content(prompt)
                    planner_text = response.text

                    # PDF generation
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, "Your Personal 7-Day Planner", ln=1, align='C')
                    pdf.ln(10)
                    pdf.set_font("Arial", '', 12)
                    for line in planner_text.split('\n'):
                        pdf.multi_cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'))

                    pdf_bytes = pdf.output(dest='S')

                    st.success("Planner forged!")
                    st.markdown("### Your Personalized Planner")
                    st.markdown(planner_text)

                    st.download_button(
                        "📅 Download Planner PDF",
                        data=pdf_bytes,
                        file_name="personalforge_planner.pdf",
                        mime="application/pdf"
                    )

                elif product == "Short Custom Ebook":
                    prompt = f"""
Write a short 1000-word custom ebook/story/guide for {name or 'me'} focused on {interests}.

Make it inspiring, personal, and valuable.
Structure with chapters and actionable advice.
"""

                    response = gemini_model.generate_content(prompt)
                    ebook_text = response.text

                    st.success("Ebook forged!")
                    st.markdown("### Your Custom Ebook")
                    st.markdown(ebook_text)

                    st.download_button(
                        "📚 Download Ebook (Text)",
                        data=ebook_text,
                        file_name="personalforge_ebook.txt",
                        mime="text/plain"
                    )

                st.caption("PersonalForge uses Gemini & Flux AI — uniquely yours.")
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")

st.markdown("---")
st.caption("PersonalForge • AI-crafted just for you • Powered by Gemini & Flux")
