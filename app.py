import streamlit as st
import google.generativeai as genai
from google.generativeai import types
from youtube_transcript_api import YouTubeTranscriptApi
import re

# --- Set up UI ---
st.set_page_config(page_title="YouTube Summarizer", page_icon="🎬")
st.title("🎬 YouTube Video Summarizer with Gemini")
st.markdown("Summarize any YouTube video using Google Gemini AI.")

# --- API Key input (as password field) ---
api_key = st.text_input("🔑 Enter your Google API Key", type="password")

if not api_key:
    st.warning("Please enter your Google API Key to continue.")
    st.stop()

# --- Configure Gemini ---
genai.configure(api_key=api_key)

# --- Helper: Extract video ID from YouTube URL ---
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

# --- Helper: Get transcript ---
def get_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([entry['text'] for entry in transcript])

# --- Helper: Summarize using Gemini ---
def summarize(text, summary_type):
    prompts = {
        "Brief (3 sentences)": "Summarize the video in 3 sentences.",
        "Full Summary": "Write a detailed summary of the video.",
        "Bullet Points": "Summarize the video in 5 concise bullet points."
    }
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([
        types.Part(text=text),
        types.Part(text=prompts[summary_type])
    ])
    return response.candidates[0].content.parts[0].text

# --- Input Fields ---
video_url = st.text_input("🎥 Enter a YouTube Video URL")
summary_type = st.selectbox("📝 Choose Summary Type", [
    "Brief (3 sentences)",
    "Full Summary",
    "Bullet Points"
])

# --- Action Button ---
if st.button("Generate Summary"):
    video_id = extract_video_id(video_url)
    if not video_id:
        st.error("Invalid YouTube URL.")
    else:
        with st.spinner("Fetching transcript..."):
            try:
                transcript_text = get_transcript(video_id)
                with st.spinner("Generating summary with Gemini..."):
                    output = summarize(transcript_text, summary_type)
                    st.success("✅ Summary generated successfully!")
                    st.markdown("### 📄 Summary:")
                    st.write(output)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
