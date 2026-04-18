import streamlit as st
import cortex, bot_standard, bot_think, bot_onion, bot_dna
from streamlit_lottie import st_lottie
import requests, pandas as pd

st.set_page_config(page_title="BDL.AI NEXUS", layout="wide")
cortex.apply_theme("cyberpunk")

# Navigation State
if "active_page" not in st.session_state: st.session_state.active_page = "Home"

with st.sidebar:
    st.title("🔑 Access Panel")
    if st.button("🌐 RETURN TO NEXUS HOME"): 
        st.session_state.active_page = "Home"
        st.rerun()
    key = st.text_input("Credentials", type="password")
    is_admin = (key in ["admin", "qwerty"])
    is_dev = (key == "qwerty")

# ROUTER LOGIC
if st.session_state.active_page == "Home":
    st.markdown("<h1>BDL.AI NEXUS GATEWAY</h1>", unsafe_allow_html=True)
    score = cortex.get_total_intelligence()
    st.markdown(f"<div class='intel-counter'><span>{score}</span><br><small>SYNTHESIZED LESSONS</small></div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='bot-card'><img src='https://img.icons8.com/neon/120/bot.png' width='100'/><h2>BDL</h2><p>The Original</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE BDL"): st.session_state.active_page = "BDL"; st.rerun()
    with c2:
        st.markdown("<div class='bot-card'><img src='https://img.icons8.com/neon/120/brain.png' width='100'/><h2>THINK</h2><p>Web Powerhouse</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE THINK"): st.session_state.active_page = "Think"; st.rerun()
    with c3:
        st.markdown("<div class='bot-card'><div class='dev-box'><div class='caution-tape'>DEV-ONLY</div><div style='font-size: 80px;'>🧅</div></div><h2>ONION</h2><p>Layer Synthesis</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE ONION"):
            if is_dev: st.session_state.active_page = "Onion"; st.rerun()
            else: st.warning("Requires Dev Key.")
    with c4:
        st.markdown("<div class='bot-card'><div style='font-size: 80px;'>🧬</div><h2>DNA</h2><p>Genealogy Scan</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE DNA"): st.session_state.active_page = "DNA"; st.rerun()

    if is_admin:
        st.markdown("<h2 style='color:#FF8C00; border-bottom:1px solid #FF8C00;'>🛠️ ADMIN COMMAND</h2>", unsafe_allow_html=True)
        # Add Admin Approval logic here (same as V10.1)

elif st.session_state.active_page == "BDL": bot_standard.run()
elif st.session_state.active_page == "Think": bot_think.run()
elif st.session_state.active_page == "Onion": bot_onion.run()
elif st.session_state.active_page == "DNA": bot_dna.run()
