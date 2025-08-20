import os
import streamlit as st

st.write("Current directory:", os.getcwd())
st.write("Files here:", os.listdir())
st.write("Files in .streamlit:", os.listdir(".streamlit") if os.path.exists(".streamlit") else "No .streamlit folder")
