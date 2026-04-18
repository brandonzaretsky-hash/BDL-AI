import
import streamlit as st
import cortex, bot_standard, bot_think, bot_onion, bot_dna
import pandas as pd

st.set_page_config(page_title="BDL.AI NEXUS", layout="wide", page_icon="🧠")
cortex.apply_theme("cyberpunk")

if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

with st.sidebar:
    st.title("🔑 Access Panel")
    if st.button("🌐 RETURN TO NEXUS HOME"): 
        st.session_state.active_page = "Home"
        st.rerun()
    key = st.text_input("Credentials", type="password")
    is_admin = (key in ["admin", "qwerty"])
    is_dev = (key == "qwerty")

page = st.session_state.active_page

if page == "Home":
    st.markdown("<h1>BDL.AI NEXUS GATEWAY</h1>", unsafe_allow_html=True)
    score = cortex.get_total_intelligence()
    st.markdown(f"<div class='intel-counter'><span>{score}</span><br><small>LESSONS IN CORTEX</small></div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='bot-card'><h2>🤖</h2><h2>BDL</h2><p>Original</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE BDL"): st.session_state.active_page = "BDL"; st.rerun()
    with c2:
        st.markdown("<div class='bot-card'><h2>🧠</h2><h2>THINK</h2><p>Web Scan</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE THINK"): st.session_state.active_page = "Think"; st.rerun()
    with c3:
        st.markdown("<div class='bot-card'><h2>🧅</h2><h2>ONION</h2><p>AI Synthesis</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE ONION"):
            if is_dev: st.session_state.active_page = "Onion"; st.rerun()
            else: st.warning("Dev Key Required.")
    with c4:
        st.markdown("<div class='bot-card'><h2>🧬</h2><h2>DNA</h2><p>Genealogy</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE DNA"): st.session_state.active_page = "DNA"; st.rerun()
elif page == "Seed": seed.run()
elif page == "BDL": bot_standard.run()
elif page == "Think": bot_think.run()
elif page == "Onion": bot_onion.run()
elif page == "DNA": bot_dna.run()
else:
    st.session_state.active_page = "Home"; st.rerun()
