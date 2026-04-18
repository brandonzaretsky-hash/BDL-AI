import streamlit as st
from utils import apply_theme, conn
import re

apply_theme("cyberpunk")
st.title("🧅 BDL Onion")

prompt = st.chat_input("Peel context...")
if prompt:
    ctx = conn.read(worksheet="Context", ttl="1s")
    # Synthesis logic here
    st.write("Onion Synthesis Active.")
