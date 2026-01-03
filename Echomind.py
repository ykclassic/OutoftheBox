# app.py
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import PyPDF2, docx, json

st.title("🧠 EchoMind")
st.caption("Understand your past self through your old words.")

uploaded_files = st.file_uploader("Upload your old content", accept_multiple_files=True, 
                                 type=['txt', 'pdf', 'docx', 'json'])

if uploaded_files:
    all_text = ""
    for file in uploaded_files:
        if file.type == "text/plain":
            all_text += file.read().decode()
        elif file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                all_text += page.extract_text()
        # Add docx, json (Twitter export) handlers...

    if all_text:
        with st.spinner("Analyzing your past self..."):
            llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
            prompt = PromptTemplate.from_template("""
            You are an empathetic analyst explaining someone's past mindset.
            Content from approximately {year}:
            {text}

            Explain why they likely thought this way, considering:
            - Their probable age and cognitive stage
            - Cultural/trend context of the time
            - Emotional tone and language patterns
            Be kind, insightful, and specific.
            """)
            chain = prompt | llm
            response = chain.invoke({"text": all_text[:10000], "year": "2015-2020"})  # Estimate year

        st.subheader("Why Your Past Self Thought This Way")
        st.write(response.content)
