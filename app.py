import streamlit as st
import os
import io
from google import genai
from google.genai import types
from google.api_core import retry
from docx import Document

# Inject full-dark CSS styles
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
    }
    .css-18e3th9, .css-1d391kg {
        background-color: #0a0a0a;
        color: #e0e0e0;
    }
    label, .stTextInput>div>div>input, .stRadio label {
        color: #e0e0e0 !important;
    }
    .stTextInput>div>div>input {
        background-color: #1a1a1a !important;
        color: #f5f5f5 !important;
    }
    .stRadio > label {
        color: #f5f5f5 !important;
    }
    .stButton > button {
        background-color: #333 !important;
        color: #e0e0e0 !important;
    }
    .stButton > button:hover {
        background-color: #555 !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="🎬 Gemini YouTube Summarizer", layout="wide")
st.title("🎥 Gemini YouTube Video Summarizer")

# Sidebar for input controls
with st.sidebar:
    st.header("Settings")

    st.markdown("### 🔑 Enter your Google API Key")
    api_key = st.text_input("", type="password")

    if not api_key and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]

    st.markdown("### 📺 Enter YouTube video URL")
    youtube_url = st.text_input("", placeholder="e.g. https://youtube.com/shorts/...")

    st.markdown("### 🤖 Choose your task")
    task = st.radio("", ["Summary (3 sentences)", "Full transcription", "Main points", "Brief explanation"])

# Main fetch button
fetch = st.button("🚀 Fetch")

# File generators
def create_txt_file(txt): return io.BytesIO(txt.encode('utf-8'))
def create_docx_file(txt):
    doc = Document()
    doc.add_paragraph(txt)
    f = io.BytesIO(); doc.save(f); f.seek(0); return f

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    client = genai.Client()
    is_retriable = lambda e: isinstance(e, genai.errors.APIError) and e.code in {429, 503}
    if not hasattr(genai.models.Models.generate_content, '__wrapped__'):
        genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(genai.models.Models.generate_content)

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
                user_prompt = prompt_map.get(task, prompt_map["Summary (3 sentences)"])
                try:
                    response = client.models.generate_content(
                        model="models/gemini-2.0-flash",
                        contents=types.Content(parts=[types.Part(file_data=types.FileData(file_uri=youtube_url)), types.Part(text=user_prompt)])
                    )
                    text = response.text
                    st.success("✅ Done!")
                    st.markdown(f"### 📋 {task}")
                    st.write(text)

                    st.download_button("📄 Download as TXT", data=create_txt_file(text), file_name="output.txt", mime="text/plain")
                    st.download_button("📄 Download as DOCX", data=create_docx_file(text), file_name="output.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
else:
    st.sidebar.warning("⚠️ Please enter your Google API key to continue.")
