import streamlit as st
from utils import apply_theme, run_deepthink_engine

apply_theme("cyberpunk")
st.title("🧠 BDL Think")
sport = st.sidebar.toggle("Sport Mode")

prompt = st.chat_input("Scan topic...")
if prompt:
    res = run_deepthink_engine(prompt, sport)
    st.markdown(res)
