import os
os.system("apt-get update && apt-get install -y ffmpeg")

import os
import streamlit as st
import whisper
import tempfile
import subprocess

# ✅ Force install ffmpeg (temporary workaround for Streamlit Cloud)
os.system("apt-get update && apt-get install -y ffmpeg")

st.title("🎤 Whisper Transcriber (No API Needed)")

# ✅ Check ffmpeg is available
try:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    st.success("✅ ffmpeg found: " + result.stdout.splitlines()[0])
except Exception as e:
    st.error(f"❌ ffmpeg NOT found: {e}")

# File uploader
uploaded_file = st.file_uploader("Upload an audio/video file", type=["mp4", "mp3", "mkv", "wav", "mov"])

@st.cache_resource
def load_model():
    return whisper.load_model("tiny")  # Use "base", "small", etc. for better accuracy

if uploaded_file:
    st.info("Transcribing...")

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # Load Whisper model
    model = load_model()

    try:
        result = model.transcribe(tmp_path)
        st.success("✅ Transcription completed!")
        st.subheader("📝 Transcript")
        st.write(result["text"])
    except Exception as e:
        st.error(f"❌ Transcription error: {e}")
    finally:
        os.remove(tmp_path)
