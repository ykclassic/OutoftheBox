import streamlit as st
import replicate
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os

# Replicate API token (secure via secrets)
try:
    replicate_client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
except KeyError:
    st.error("Replicate API token not found. Add REPLICATE_API_TOKEN to Streamlit secrets.")
    st.stop()

st.set_page_config(page_title="AfroForge", page_icon="🌍", layout="wide")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#ff6b35; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🌍 AfroForge</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">AI-powered Afrocentric print-on-demand designs • Global culture, forged fresh.</p>', unsafe_allow_html=True)

st.info("Describe an Afrocentric design idea. AfroForge generates artwork optimized for clothing, art, and accessories.")

prompt = st.text_area(
    "Design idea",
    height=150,
    placeholder="e.g., Modern Ankara pattern t-shirt with Adinkra wisdom symbols and vibrant colors"
)

style = st.selectbox("Style vibe", [
    "Vibrant and bold",
    "Minimalist and elegant",
    "Traditional with modern twist",
    "Streetwear urban",
    "Abstract geometric"
])

num_variants = st.slider("Number of variants", 1, 4, 2)

if st.button("Forge Designs", type="primary"):
    if not prompt.strip():
        st.warning("Enter a design idea first.")
    else:
        full_prompt = f"Afrocentric print-on-demand design: {prompt}. {style}. High resolution, suitable for t-shirts, hoodies, posters. Rich African cultural elements, patterns, symbols."

        with st.spinner("Forging your Afrocentric designs..."):
            try:
                outputs = replicate_client.run(
                    "black-forest-labs/flux-dev",
                    input={
                        "prompt": full_prompt,
                        "num_outputs": num_variants,
                        "aspect_ratio": "1:1",
                        "output_format": "png"
                    }
                )

                st.success("Designs forged!")
                cols = st.columns(num_variants)

                for idx, output_url in enumerate(outputs):
                    with cols[idx]:
                        response = requests.get(output_url)
                        img = Image.open(BytesIO(response.content))

                        # Simple mockup: white t-shirt background
                        tshirt = Image.new("RGB", (600, 800), "white")
                        img_resized = img.resize((400, 400))
                        tshirt.paste(img_resized, (100, 150))

                        st.image(tshirt, caption=f"Variant {idx+1} on T-Shirt Mockup")
                        st.download_button(
                            f"Download Variant {idx+1}",
                            data=response.content,
                            file_name=f"afroforge_variant_{idx+1}.png",
                            mime="image/png"
                        )

                st.caption("AfroForge uses Flux AI via Replicate — designs are AI-generated and royalty-free for POD use.")
            except Exception as e:
                st.error(f"Design generation failed: {str(e)}")

st.markdown("---")
st.caption("AfroForge • Celebrate African culture through AI-crafted designs • Global fulfillment coming soon")
