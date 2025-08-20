import streamlit as st
import os
import io
from google import genai
from google.genai import types
from google.api_core import retry
from docx import Document
import whisper
import tempfile

st.set_page_config(page_title="Gemini + Whisper Video Summarizer", layout="wide")
st.title("🎥 Gemini + Whisper Video Summarizer")

# Load Whisper model WITHOUT caching to avoid errors on Streamlit Cloud
def load_whisper_model():
    return whisper.load_model("base")

model = load_whisper_model()

# Sidebar inputs
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Google API Key", type="password")
    if not api_key and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]

    task = st.radio("Choose task:", ["Summary (3 sentences)", "Full transcription", "Main points", "Brief explanation"])

# Tabs for YouTube URL or file upload
tab1, tab2 = st.tabs(["📺 YouTube URL", "📁 Upload Video"])

fetch = False
text_output = ""

with tab1:
    youtube_url = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...")
    if st.button("🚀 Fetch from YouTube"):
        fetch = True
        video_source = "youtube"
        file_uri = youtube_url

with tab2:
    uploaded_file = st.file_uploader("Upload video file", type=["mp4", "mov", "avi", "mkv"])
    if uploaded_file is not None and st.button("🚀 Transcribe & Summarize Upload"):
        fetch = True
        video_source = "upload"

def create_txt_file(text):
    return io.BytesIO(text.encode('utf-8'))

def create_docx_file(text):
    doc = Document()
    doc.add_paragraph(text)
    f = io.BytesIO()
    doc.save(f)
    f.seek(0)
    return f

def transcribe_video(file_path):
    result = model.transcribe(file_path)
    return result["text"]

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    client = genai.Client()

    # Retry logic for Gemini API
    is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})
    if not hasattr(genai.models.Models.generate_content, '__wrapped__'):
        genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(
            genai.models.Models.generate_content
        )

    if fetch:
        prompt_map = {
            "Summary (3 sentences)": "Please summarize the video in 3 sentences.",
            "Full transcription": "Provide a full transcription of the video.",
            "Main points": "What are the key points or takeaways from this video?",
            "Brief explanation": "Briefly explain what this video is about."
        }
        user_prompt = prompt_map.get(task, "Please summarize the video.")

        try:
            if video_source == "youtube":
                with st.spinner("Processing YouTube video with Gemini..."):
                    response = client.models.generate_content(
                        model='models/gemini-2.0-flash',
                        contents=types.Content(
                            parts=[
                                types.Part(file_data=types.FileData(file_uri=file_uri)),
                                types.Part(text=user_prompt)
                            ]
                        )
                    )
                    text_output = response.text

            elif video_source == "upload":
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_filepath = tmp_file.name

                with st.spinner("Transcribing uploaded video with Whisper..."):
                    transcript = transcribe_video(tmp_filepath)

                os.remove(tmp_filepath)

                with st.spinner("Processing transcript with Gemini..."):
                    response = client.models.generate_content(
                        model='models/gemini-2.0-flash',
                        contents=types.Content(
                            parts=[
                                types.Part(text=f"{user_prompt}\n\nTranscript:\n{transcript}")
                            ]
                        )
                    )
                    text_output = response.text

            st.success("✅ Done!")
            st.markdown(f"### 📋 {task}")
            st.write(text_output)

            txt_file = create_txt_file(text_output)
            docx_file = create_docx_file(text_output)

            st.download_button("📄 Download TXT", data=txt_file, file_name="output.txt", mime="text/plain")
            st.download_button("📄 Download DOCX", data=docx_file, file_name="output.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

else:
    st.sidebar.warning("⚠️ Please enter your Google API key to continue.")
