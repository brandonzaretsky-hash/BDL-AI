import streamlit as st
from utils import apply_theme, get_total_intelligence, conn
from streamlit_lottie import st_lottie
import requests, pandas as pd

st.set_page_config(page_title="BDL.AI NEXUS", layout="wide")
apply_theme("cyberpunk")

with st.sidebar:
    st.title("🔑 Access Panel")
    key = st.text_input("Credentials", type="password")
    is_admin = (key == "admin" or key == "qwerty")

st.markdown("<h1>BDL.AI NEXUS GATEWAY</h1>", unsafe_allow_html=True)
score = get_total_intelligence()
st.markdown(f"<div class='intel-counter'><span>{score}</span><br><small>SYNTHESIZED LESSONS</small></div>", unsafe_allow_html=True)

st.info("👈 SELECT A MODULE IN THE SIDEBAR TO PLUG-IN")

if is_admin:
    st.markdown("<h2 class='admin-header'>🛠️ ADMIN TERMINAL</h2>", unsafe_allow_html=True)
    # Put your Requests approval logic here
