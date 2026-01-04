import streamlit as st
from google.generativeai import GenerativeModel, configure

# Secure Gemini API key
try:
    configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

model = GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="AffiliateForge", page_icon="💰", layout="wide")

st.markdown("""
<style>
    .big-font { font-size:50px !important; font-weight:bold; text-align:center; color:#f1c40f; }
    .subheader { font-size:24px; color:#cccccc; text-align:center; margin-bottom:40px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">💰 AffiliateForge</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">AI-generated product reviews for affiliate commissions.</p>', unsafe_allow_html=True)

st.info("Describe a product and paste your affiliate link. AffiliateForge generates persuasive, balanced reviews ready for your blog, YouTube, or social.")

with st.form("review_form"):
    product_name = st.text_input("Product Name")
    description = st.text_area("Product Description (features, benefits)", height=150)
    affiliate_link = st.text_input("Your Affiliate Link", placeholder="e.g., https://amazon.com/dp/B123?tag=yourtag")
    
    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox("Review Style", ["Enthusiastic Buyer", "Balanced Analyst", "Comparative (vs competitor)", "Storytelling"])
    with col2:
        length = st.selectbox("Review Length", ["Short (300 words)", "Medium (600 words)", "Long (1000 words)"])

    submitted = st.form_submit_button("Generate Review")

if submitted:
    if not product_name or not affiliate_link:
        st.warning("Product name and affiliate link required.")
    else:
        with st.spinner("Forging your affiliate review..."):
            try:
                prompt = f"""
You are AffiliateForge — an expert affiliate marketer writing high-converting product reviews.

Product: {product_name}
Description: {description}
Affiliate link: {affiliate_link}

Write a {length.lower()} review in this style: {style}

Include:
- Engaging intro hook
- Key features and benefits
- Pros and cons (balanced)
- Personal "why I love it" touch
- Natural call-to-action with the affiliate link
- SEO-friendly (natural keywords)

Make it persuasive but honest. Format with markdown headings and bullets.
"""

                response = model.generate_content(prompt)
                review = response.text

                st.success("Review Generated")
                st.markdown("### Your Affiliate Review")
                st.markdown(review)

                # Copy button + affiliate link reminder
                st.code(review, language="markdown")
                st.download_button(
                    "📥 Download Review (Markdown)",
                    review,
                    "affiliate_review.md",
                    "text/markdown"
                )

                st.caption("AffiliateForge uses Gemini AI — always disclose affiliate links per FTC guidelines.")
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")

st.markdown("---")
st.caption("AffiliateForge • Turn products into commissions with AI • Powered by Gemini AI")
