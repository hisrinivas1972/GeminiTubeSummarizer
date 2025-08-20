import streamlit as st
import subprocess

st.title("ffmpeg check")

try:
    res = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    st.write("✅ ffmpeg version:", res.stdout.splitlines()[0])
except Exception as e:
    st.error(f"❌ ffmpeg NOT found: {e}")
