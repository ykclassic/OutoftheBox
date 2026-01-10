import streamlit as st
import requests
from PIL import Image
import io
import os

# ─── CONFIG ───────────────────────────────────────────────────────────────
API_KEY = "AkeMEkvNPdCEXEQEJc1b9Bjs"           # ← Your remove.bg API key
API_URL = "https://api.remove.bg/v1.0/removebg"

st.set_page_config(
    page_title="Background Remover & Replacer",
    page_icon="🖼️",
    layout="wide"
)

# ─── FUNCTIONS ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)  # cache results for 1 hour
def remove_background(image_bytes):
    """Call remove.bg API and return image without background (PNG)"""
    headers = {
        "X-Api-Key": API_KEY
    }
    files = {
        "image_file": ("image.png", image_bytes, "image/png")
    }
    data = {
        "size": "auto",
        "format": "png",
        "type": "auto"
    }

    try:
        response = requests.post(API_URL, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            return response.content
        else:
            error = response.json().get("errors", [{}])[0].get("title", "Unknown error")
            st.error(f"API Error ({response.status_code}): {error}")
            return None
            
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None


def replace_background(original_no_bg_bytes, bg_image):
    """Place transparent image on new background"""
    try:
        fg = Image.open(io.BytesIO(original_no_bg_bytes)).convert("RGBA")
        bg = bg_image.convert("RGBA").resize(fg.size, Image.LANCZOS)
        
        # Composite: background + foreground
        combined = Image.alpha_composite(bg, fg)
        return combined
    except Exception as e:
        st.error(f"Background replacement failed: {str(e)}")
        return None


# ─── UI ────────────────────────────────────────────────────────────────────
st.title("🖼️ Background Remover & Replacer")
st.markdown("Powered by **remove.bg** API")

# ── Upload image ──────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload your image (PNG/JPG/WEBP)",
    type=["png", "jpg", "jpeg", "webp"],
    help="Max size ~5MB recommended (remove.bg free tier limit)"
)

if uploaded_file is not None:
    # Show original
    original_bytes = uploaded_file.read()
    original_img = Image.open(io.BytesIO(original_bytes))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original")
        st.image(original_img, use_column_width=True)
    
    # ── Processing options ────────────────────────────────────────────────
    st.markdown("### What would you like to do?")
    
    option = st.radio("", 
        ["Remove background only", "Replace background"], 
        horizontal=True,
        key="mode"
    )

    result_bytes = None
    processed_img = None

    # ── Remove background ─────────────────────────────────────────────────
    if st.button("✂️ Process Image", type="primary", use_container_width=True):
        with st.spinner("Removing background... (usually 3–8 seconds)"):
            result_bytes = remove_background(original_bytes)
            
            if result_bytes:
                processed_img = Image.open(io.BytesIO(result_bytes))
                
                with col2:
                    st.subheader("Result")
                    st.image(processed_img, use_column_width=True)
                
                # Download button for transparent PNG
                st.download_button(
                    label="⬇️ Download Transparent PNG",
                    data=result_bytes,
                    file_name=f"no_background_{uploaded_file.name.split('.')[0]}.png",
                    mime="image/png",
                    use_container_width=True
                )

    # ── Replace background ────────────────────────────────────────────────
    if option == "Replace background" and result_bytes is not None:
        st.markdown("### Choose or upload new background")
        
        bg_option = st.radio("Background source", 
            ["Solid color", "Upload your own background"],
            horizontal=True
        )

        bg_image = None
        
        if bg_option == "Solid color":
            color = st.color_picker("Pick background color", "#00ff9d")
            bg_image = Image.new("RGBA", processed_img.size, color + "ff")  # with alpha
        else:
            bg_upload = st.file_uploader("Upload background image", 
                                        type=["png","jpg","jpeg"], 
                                        key="bg_upload")
            if bg_upload:
                bg_image = Image.open(bg_upload)

        if bg_image and st.button("🔄 Apply New Background"):
            with st.spinner("Compositing new background..."):
                final_img = replace_background(result_bytes, bg_image)
                if final_img:
                    final_bytes = io.BytesIO()
                    final_img.save(final_bytes, format="PNG")
                    final_bytes = final_bytes.getvalue()

                    st.subheader("Final Result")
                    st.image(final_img, use_column_width=True)

                    st.download_button(
                        label="⬇️ Download Final Image",
                        data=final_bytes,
                        file_name=f"with_new_bg_{uploaded_file.name.split('.')[0]}.png",
                        mime="image/png",
                        use_container_width=True
                    )

st.markdown("---")
st.caption("Note: Free remove.bg API has limitations (50 credits/month, ~625×400px max resolution). "
           "For production use consider upgrading your plan.")
