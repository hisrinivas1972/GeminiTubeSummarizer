import streamlit as st
import os
import io
from google import genai
from google.genai import types
from google.api_core import retry
from docx import Document
from fpdf import FPDF

# ... your existing CSS and sidebar inputs code ...

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
    # Split text by lines for pdf writing
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    f = io.BytesIO()
    pdf.output(f)
    f.seek(0)
    return f

# ... after you get `response.text` in your try block:

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
