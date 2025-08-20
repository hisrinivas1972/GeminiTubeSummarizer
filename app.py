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
    .css-1v3fvcr h1 {
        text-align: center;
        color: #e0e0e0;
        margin-bottom: 40px;
    }
    .css-1d391kg {
        background-color: #121212;
        color: #ddd !important;
    }
    label, .stRadio > label, .css-1x8cf1d {
        color: #ddd !important;
    }
    .css-18e3th9 {
        background-color: #121212;
    }
    .css-1d391kg, .css-18e3th9 {
        color: #ddd;
    }
    .stButton>button {
        background-color: #333 !important;
        color: #ddd !important;
        border: none !important;
    }
    .stButton>button:hover {
        background-color: #555 !important;
        color: white !important;
    }
    .css-1aumxhk h4 {
        color: #ddd !important;
        margin-bottom: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.set_page_config(page_title="🎬 Gemini Video Summarizer", layout="wide")
st.title("🎥 Gemini Video Summarizer")

# Sidebar
with st.sidebar:
    st.header("Settings")

    st.markdown("#### 🔑 Enter your Google API Key", unsafe_allow_html=True)
    api_key = st.text_input("", type="password")

    if not api_key and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]

    st.markdown("#### 🤖 Choose what you want to do:", unsafe_allow_html=True)
    task = st.radio("", ["Summary (3 sentences)", "Full transcription", "Main points", "Brief explanation"])

# Create tabs
tab1, tab2, tab3 = st.tabs(["📺 YouTube Link", "📁 Upload Video", "📂 Google Drive Link"])

fetch = False
video_source = None
file_uri = None

# Tab 1: YouTube
with tab1:
    youtube_url = st.text_input("📺 Enter YouTube URL", placeholder="e.g. https://youtube.com/watch?v=...")
    fetch_youtube = st.button("🚀 Fetch from YouTube")
    if fetch_youtube:
        fetch = True
        video_source = "youtube"
        file_uri = youtube_url

# Tab 2: Upload (Not supported directly)
with tab2:
    st.warning("⚠️ Gemini cannot process raw uploaded video files directly. Use YouTube or Google Drive.")
    uploaded_video = st.file_uploader("📁 Upload a video file", type=["mp4", "mov", "avi", "mkv"])

# Tab 3: Google Drive
with tab3:
    gdrive_url = st.text_input("📂 Paste Google Drive public link")
    fetch_drive = st.button("🚀 Fetch from Google Drive")

    def convert_drive_link(drive_url):
        try:
            file_id = drive_url.split("/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        except Exception:
            return None

    if fetch_drive:
        fetch = True
        video_source = "gdrive"
        file_uri = convert_drive_link(gdrive_url)

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

    is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})
    if not hasattr(genai.models.Models.generate_content, '__wrapped__'):
        genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(
            genai.models.Models.generate_content
        )

    if fetch:
        if not file_uri:
            st.error("❌ Invalid or missing video link.")
        else:
            with st.spinner("Processing with Gemini..."):
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
                                types.Part(file_data=types.FileData(file_uri=file_uri)),
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
