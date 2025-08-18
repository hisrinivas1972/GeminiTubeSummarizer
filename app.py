import streamlit as st
import os
from google import genai
from google.genai import types
from google.api_core import retry

# Set dark theme via Streamlit config (in .streamlit/config.toml or programmatically)
# We'll add a simple CSS override here for dark mode and centering

# Inject CSS for dark mode and centering title & inputs colors
st.markdown(
    """
    <style>
    /* Center the main title */
    .css-1v3fvcr h1 {
        text-align: center;
        color: #e0e0e0;
        margin-bottom: 40px;
    }
    /* Sidebar background & text */
    .css-1d391kg {
        background-color: #121212;
        color: #ddd !important;
    }
    /* Sidebar inputs label color */
    label, .stRadio > label, .css-1x8cf1d {
        color: #ddd !important;
    }
    /* Main area background */
    .css-18e3th9 {
        background-color: #121212;
    }
    /* Main text color */
    .css-1d391kg, .css-18e3th9 {
        color: #ddd;
    }
    /* Buttons */
    .stButton>button {
        background-color: #333 !important;
        color: #ddd !important;
        border: none !important;
    }
    .stButton>button:hover {
        background-color: #555 !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Set page config with wide layout (optional)
st.set_page_config(page_title="🎬 Gemini YouTube Summarizer", layout="wide")

# Title centered in main area
st.title("🎥 Gemini YouTube Video Summarizer")

# Sidebar inputs
with st.sidebar:
    st.header("Settings")

    # Input Google API Key securely
    api_key = st.text_input("🔑 Enter your Google API Key", type="password")

    # Use secret if set
    if not api_key and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]

    youtube_url = st.text_input("📺 Enter YouTube video URL")

    task = st.radio(
        "🤖 Choose what you want to do:",
        ["Summary (3 sentences)", "Full transcription", "Main points", "Brief explanation"]
    )

    fetch = st.button("🚀 Fetch")

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

    if fetch:
        if not youtube_url:
            st.sidebar.warning("Please enter a YouTube URL.")
        else:
            with st.spinner("Processing..."):
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
    st.sidebar.warning("⚠️ Please enter your Google API key to continue.")
