"""Background removal tool with bounded uploads and secret-safe provider errors."""

from __future__ import annotations

import hashlib
import io
import os
from typing import Optional

import requests
import streamlit as st
from PIL import Image, UnidentifiedImageError

API_URL = "https://api.remove.bg/v1.0/removebg"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
REQUEST_TIMEOUT_SECONDS = (5, 30)
ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP"}


def get_api_key() -> Optional[str]:
    """Read the provider key from Streamlit secrets or the environment."""
    try:
        value = st.secrets.get("REMOVE_BG_API_KEY")
    except (AttributeError, FileNotFoundError):
        value = None
    return value or os.getenv("REMOVE_BG_API_KEY")


def decode_image(image_bytes: bytes) -> Image.Image:
    """Validate and decode an uploaded image under conservative resource limits."""
    if not image_bytes:
        raise ValueError("The uploaded image is empty.")
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError("Each image must be 5 MB or smaller.")

    try:
        with Image.open(io.BytesIO(image_bytes)) as source:
            if source.format not in ALLOWED_FORMATS:
                raise ValueError("Upload a PNG, JPEG, or WEBP image.")
            width, height = source.size
            if width <= 0 or height <= 0 or width * height > MAX_IMAGE_PIXELS:
                raise ValueError("The image dimensions exceed the supported limit.")
            source.verify()

        with Image.open(io.BytesIO(image_bytes)) as source:
            source.load()
            return source.convert("RGBA")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("The file is not a valid supported image.") from exc


def remove_background(image_bytes: bytes, api_key: str) -> bytes:
    """Call remove.bg with bounded network time and sanitized errors."""
    response = None
    try:
        response = requests.post(
            API_URL,
            headers={"X-Api-Key": api_key},
            files={"image_file": ("upload.png", image_bytes, "application/octet-stream")},
            data={"size": "auto", "format": "png", "type": "auto"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code != 200:
            # Do not expose raw provider response bodies or request details.
            raise RuntimeError(
                "The background-removal provider could not process this image. "
                f"Provider status: {response.status_code}."
            )
        if not response.content:
            raise RuntimeError("The provider returned an empty result.")
        # Confirm the provider response is a decodable image before displaying it.
        result = decode_provider_png(response.content)
        return result
    except requests.Timeout as exc:
        raise RuntimeError("The provider request timed out. Please try again.") from exc
    except requests.RequestException as exc:
        raise RuntimeError("The provider is temporarily unreachable. Please try again.") from exc
    finally:
        if response is not None:
            response.close()


def decode_provider_png(image_bytes: bytes) -> bytes:
    """Validate the provider output and return a normalized PNG."""
    try:
        with Image.open(io.BytesIO(image_bytes)) as source:
            width, height = source.size
            if width <= 0 or height <= 0 or width * height > MAX_IMAGE_PIXELS:
                raise ValueError("Provider output exceeds the supported dimensions.")
            source.load()
            output = io.BytesIO()
            source.convert("RGBA").save(output, format="PNG")
            return output.getvalue()
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError("The provider returned an invalid image.") from exc


def composite_background(foreground_bytes: bytes, background: Image.Image) -> Image.Image:
    """Composite a transparent foreground over a selected background."""
    foreground = decode_image(foreground_bytes)
    resized_background = background.convert("RGBA").resize(
        foreground.size, Image.Resampling.LANCZOS
    )
    return Image.alpha_composite(resized_background, foreground)


st.set_page_config(
    page_title="Background Remover & Replacer",
    page_icon="🖼️",
    layout="wide",
)

st.title("🖼️ Background Remover & Replacer")
st.caption("Powered by remove.bg. Uploaded images are processed when you request it.")

api_key = get_api_key()
if not api_key:
    st.warning(
        "Background removal is not configured. Add REMOVE_BG_API_KEY to Streamlit "
        "secrets or the deployment environment to enable this tool."
    )
    st.stop()

uploaded_file = st.file_uploader(
    "Upload your image (PNG/JPG/WEBP)",
    type=["png", "jpg", "jpeg", "webp"],
    help="Maximum upload size: 5 MB. Maximum decoded image size: 20 megapixels.",
)

if uploaded_file is not None:
    try:
        original_bytes = uploaded_file.getvalue()
        source_digest = hashlib.sha256(original_bytes).hexdigest()
        original_image = decode_image(original_bytes)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    original_column, result_column = st.columns(2)
    with original_column:
        st.subheader("Original")
        st.image(original_image, use_container_width=True)

    option = st.radio(
        "Output",
        ["Remove background only", "Replace background"],
        horizontal=True,
    )

    if st.button("✂️ Process image", type="primary", use_container_width=True):
        try:
            with st.spinner("Removing background…"):
                processed_bytes = remove_background(original_bytes, api_key)
            st.session_state["bgforge_processed_bytes"] = processed_bytes
            st.session_state["bgforge_source_digest"] = source_digest
            st.session_state["bgforge_source_name"] = uploaded_file.name.rsplit(".", 1)[0]
            st.success("Background removed.")
        except (RuntimeError, ValueError) as exc:
            st.session_state.pop("bgforge_processed_bytes", None)
            st.error(str(exc))

    processed_bytes = (
        st.session_state.get("bgforge_processed_bytes")
        if st.session_state.get("bgforge_source_digest") == source_digest
        else None
    )
    if processed_bytes:
        with result_column:
            st.subheader("Transparent result")
            st.image(processed_bytes, use_container_width=True)
            st.download_button(
                "⬇️ Download transparent PNG",
                data=processed_bytes,
                file_name=f"no_background_{st.session_state.get('bgforge_source_name', 'image')}.png",
                mime="image/png",
                use_container_width=True,
            )

        if option == "Replace background":
            st.markdown("### Replace the background")
            background_mode = st.radio(
                "Background source",
                ["Solid color", "Upload background image"],
                horizontal=True,
            )
            background_image = None
            if background_mode == "Solid color":
                color = st.color_picker("Background color", "#00ff9d")
                background_image = Image.new("RGBA", original_image.size, color)
            else:
                background_upload = st.file_uploader(
                    "Upload background image",
                    type=["png", "jpg", "jpeg", "webp"],
                    key="bgforge_background_upload",
                )
                if background_upload is not None:
                    try:
                        background_image = decode_image(background_upload.getvalue())
                    except ValueError as exc:
                        st.error(str(exc))

            if background_image is not None and st.button("Apply new background"):
                try:
                    final_image = composite_background(processed_bytes, background_image)
                    output = io.BytesIO()
                    final_image.save(output, format="PNG")
                    final_bytes = output.getvalue()
                    st.image(final_image, use_container_width=True)
                    st.download_button(
                        "⬇️ Download final image",
                        data=final_bytes,
                        file_name=f"with_new_bg_{st.session_state.get('bgforge_source_name', 'image')}.png",
                        mime="image/png",
                        use_container_width=True,
                    )
                except (RuntimeError, ValueError) as exc:
                    st.error(str(exc))

st.divider()
st.caption(
    "Provider usage may incur charges or be subject to quotas. Review the provider's "
    "terms before uploading sensitive images."
)
