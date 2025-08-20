import streamlit as st
import subprocess

st.title("🐍 Whisper + ffmpeg Debug Demo")

# Check if ffmpeg is available
try:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    st.write("✅ ffmpeg found:", result.stdout.splitlines()[0])
except Exception as e:
    st.error(f"❌ ffmpeg check error: {e}")

# Try to import whisper and load model
try:
    import whisper
    st.write("✅ whisper package imported")

    @st.cache_resource
    def load_model():
        return whisper.load_model("tiny")  # lighter model to test

    model = load_model()
    st.success("✅ Whisper 'tiny' model loaded successfully!")

except Exception as e:
    st.error(f"❌ Error loading whisper model: {e}")
