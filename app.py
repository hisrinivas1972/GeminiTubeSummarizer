import streamlit as st
import whisper
import tempfile
import os
import subprocess

st.title("🎤 Whisper Video/Audio Transcriber")

# Check if ffmpeg is installed
try:
    ffmpeg_version = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    st.sidebar.success(f"✅ ffmpeg found: {ffmpeg_version.stdout.splitlines()[0]}")
except Exception as e:
    st.sidebar.error(f"❌ ffmpeg NOT found: {e}")

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

    try:
        # Run transcription
        result = model.transcribe(temp_file_path)
        transcript = result["text"]

        st.subheader("📝 Transcript")
        st.write(transcript)
    except Exception as e:
        st.error(f"❌ Transcription error: {e}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
