import streamlit as st
import os
from google import genai
from google.genai import types
from google.api_core import retry

# API Key input (hide input)
api_key = st.text_input("🔑 Enter your Google API Key", type="password")

# Use Streamlit secret if available
if not api_key and "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

# Proceed if API key is available
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    client = genai.Client()

    # Retry on quota errors
    is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})
    if not hasattr(genai.models.Models.generate_content, '__wrapped__'):
        genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(
            genai.models.Models.generate_content
        )

    st.title("🎬 Gemini-Powered YouTube Video Summarizer")
    youtube_url = st.text_input("📺 YouTube Video URL")

    if youtube_url:
        with st.spinner("⏳ Summarizing video..."):
            try:
                response = client.models.generate_content(
                    model='models/gemini-2.0-flash',
                    contents=types.Content(
                        parts=[
                            types.Part(file_data=types.FileData(file_uri=youtube_url)),
                            types.Part(text="Please summarize the video in 3 sentences.")
                        ]
                    )
                )
                st.success("✅ Summary generated!")
                st.write(response.text)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
else:
    st.warning("⚠️ Please enter your Google API key to continue.")
