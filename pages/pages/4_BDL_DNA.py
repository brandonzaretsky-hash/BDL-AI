import streamlit as st
from utils import apply_theme
import wikipedia, wikipediaapi

apply_theme("cyberpunk")
st.title("🧬 BDL DNA")

target = st.text_input("Name for Genealogy Scan")
if st.button("Scan") and target:
    # Genealogy logic here
    st.success(f"Scanning DNA for {target}...")
