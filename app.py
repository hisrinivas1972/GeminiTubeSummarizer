import streamlit as st
import whisper
import tempfile
import os

st.title("🎤 Whisper Video/Audio Transcriber")

uploaded_file = st.file_uploader("Upload a video or audio file", type=["mp4", "mkv", "mp3", "wav", "mov"])

@st.cache_resource
def load_model():
    return whisper.load_model("tiny")  # lightweight model for faster transcription

if uploaded_file:
    model = load_model()
    
    # Save uploaded file to temp file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    st.info("Transcribing... this may take a while depending on file size and model.")

    # Run transcription
    result = model.transcribe(temp_file_path)
    transcript = result["text"]

    st.subheader("📝 Transcript")
    st.write(transcript)

    # Clean up temp file
    os.remove(temp_file_path)
