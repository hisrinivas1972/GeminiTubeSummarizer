import streamlit as st
import os
import io
from google import genai
from google.genai import types
from google.api_core import retry
from docx import Document
from fpdf import FPDF

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

st.set_page_config(page_title="🎬 Gemini YouTube Summarizer", layout="wide")

# Title centered
st.title("🎥 Gemini YouTube Video Summarizer")

# Sidebar inputs
with st.sidebar:
    st.header("Settings")

    api_key = st.text_input("🔑 Enter your Google API Key", type="password")

    if not api_key and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]

    youtube_url = st.text_input("📺 Enter YouTube video URL")

    task = st.radio(
        "🤖 Choose what you want to do:",
        ["Summary (3 sentences)", "Full transcription", "Main points", "Brief explanation"]
    )

# Fetch button outside sidebar for global scope access
fetch = st.button("🚀 Fetch")

# Helper functions to create downloadable files
def create_txt_file(text):
    return io.BytesIO(text.encode('utf-8'))

def create_docx_file(text):
    doc = Document()
    doc.add_paragraph(text)
    f = io.BytesIO()
    doc.save(f)
    f.seek(0)
    return f

def create_pdf_file(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    f = io.BytesIO()
    pdf.output(f)
    f.seek(0)
    return f

# Main logic
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    client = genai.Client()

    # Retry on quota errors
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

                    # Download buttons
                    txt_file = create_txt_file(text)
                    docx_file = create_docx_file(text)
                    pdf_file = create_pdf_file(text)

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
                    st.download_button(
                        label="📄 Download as PDF",
                        data=pdf_file,
                        file_name="output.pdf",
                        mime="application/pdf"
                    )

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
else:
    st.sidebar.warning("⚠️ Please enter your Google API key to continue.")
