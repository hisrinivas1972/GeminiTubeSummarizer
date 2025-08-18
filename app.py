import streamlit as st
import os
from google import genai
from google.genai import types
from google.api_core import retry

# Title
st.set_page_config(page_title="🎬 Gemini YouTube Summarizer")
st.title("🎥 Gemini YouTube Video Summarizer")

# Input Google API Key securely
api_key = st.text_input("🔑 Enter your Google API Key", type="password")

# Use secret if set
if not api_key and "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

# Proceed only if API key is available
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    client = genai.Client()

    # Retry handling
    is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})
    if not hasattr(genai.models.Models.generate_content, '__wrapped__'):
        genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(
            genai.models.Models.generate_content
        )

    # Input fields
    youtube_url = st.text_input("📺 Enter a public YouTube video URL")

    task = st.radio(
        "🤖 Choose what you want to do:",
        ["Summary (3 sentences)", "Full transcription", "Main points", "Brief explanation"]
    )

    if st.button("🚀 Fetch"):
        if not youtube_url:
            st.warning("Please enter a YouTube URL.")
        else:
            with st.spinner("Processing..."):
                # Map task to actual prompt
                prompt_map = {
                    "Summary (3 sentences)": "Please summarize the video in 3 sentences.",
                    "Full transcription": "Provide a full transcription of the video.",
                    "Main points": "What are the key points or takeaways from this video?",
                    "Brief explanation": "Briefly explain what this video is about."
                }

                user_prompt = prompt_map.get(task, "Please summarize the video.")

                try:
                    response = client.models.generate_content(
                        model='models/gemini-2.0-flash',
                        contents=types.Content(
                            parts=[
                                types.Part(file_data=types.FileData(file_uri=youtube_url)),
                                types.Part(text=user_prompt)
                            ]
                        )
                    )
                    st.success("✅ Done!")
                    st.markdown(f"### 📋 {task}")
                    st.write(response.text)

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
else:
    st.warning("⚠️ Please enter your Google API key to continue.")
