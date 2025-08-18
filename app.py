import streamlit as st
import os
import io
from google import genai
from google.genai import types
from google.api_core import retry
from docx import Document

# --- Dark theme CSS + Centered Title ---
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
    /* Sidebar labels and radio text */
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
    /* Streamlit markdown headings in sidebar */
    .css-1aumxhk h4 {
        color: #ddd !important;
        margin-bottom: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.set_page_config(page_title="🎬 Gemini YouTube Summarizer", layout="wide")
st.title("🎥 Gemini YouTube Video Summarizer")

# Sidebar inputs with separated markdown labels for better emoji+text styling
with st.sidebar:
    st.header("Settings")

    st.markdown("#### 🔑 Enter your Google API Key", unsafe_allow_html=True)
    api_key = st.text_input("", type="password")

    if not api_key and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]

    st.markdown("#### 📺 Enter YouTube video URL", unsafe_allow_html=True)
    youtube_url = st.text_input("", placeholder="e.g. https://youtube.com/shorts/aAznmTycQyM?feature=share")

    st.markdown("#### 🤖 Choose what you want to do:", unsafe_allow_html=True)
    task = st.radio("", ["Summary (3 sentences)", "Full transcription", "Main points", "Brief explanation"])

    st.caption("ℹ️ Example test URL: [https://youtube.com/shorts/aAznmTycQyM](https://youtube.com/shorts/aAznmTycQyM)")

# Fetch button
fetch = st.button("🚀 Fetch")

# Helper functions
def create_txt_file(text):
    return io.BytesIO(text.encode('utf-8'))

def create_docx_file(text):
    doc = Document()
    doc.add_paragraph(text)
    f = io.BytesIO()
    doc.save(f)
    f.seek(0)
    return f

# Main logic
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    client = genai.Client()

    # Retry logic for quota errors
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
                    text = response.text

                    st.success("✅ Done!")
                    st.markdown(f"### 📋 {task}")
                    st.write(text)

                    # Downloads
                    txt_file = create_txt_file(text)
                    docx_file = create_docx_file(text)

                    st.download_button(
                        label="📄 Download as TXT",
                        data=txt_file,
                        file_name="output.txt",
                        mime="text/plain"
                    )
                    st.download_button(
                        label="📄 Download as DOCX",
                        data=docx_file,
                        file_name="output.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
else:
    st.sidebar.warning("⚠️ Please enter your Google API key to continue.")
