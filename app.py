import streamlit as st
import cortex, bot_standard, bot_think, bot_onion, bot_dna
import pandas as pd
from streamlit_lottie import st_lottie
import requests

# 1. Page Configuration (Must be the very first Streamlit command)
st.set_page_config(page_title="BDL.AI NEXUS", layout="wide", page_icon="🧠")

# 2. Apply the Theme from the Cortex
cortex.apply_theme("cyberpunk")

# 3. Initialize Session State (Prevents the Black Screen)
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

# 4. Sidebar Navigation & Access
with st.sidebar:
    st.title("🔑 Access Panel")
    if st.button("🌐 RETURN TO NEXUS HOME"): 
        st.session_state.active_page = "Home"
        st.rerun()
    
    access_key = st.text_input("Enter Credentials", type="password")
    is_admin = (access_key in ["admin", "qwerty"])
    is_dev = (access_key == "qwerty")
    st.markdown("---")
    st.caption("BDL-AI Nexus V10.6 | Super-Dev Mode Active" if is_dev else "BDL-AI Nexus V10.6")

# 5. The Router Logic
page = st.session_state.active_page

if page == "Home":
    st.markdown("<h1>BDL.AI NEXUS GATEWAY</h1>", unsafe_allow_html=True)
    
    # Intelligence Counter
    score = cortex.get_total_intelligence()
    st.markdown(f"<div class='intel-counter'><span>{score}</span><br><small>SYNTHESIZED LESSONS IN CORTEX</small></div>", unsafe_allow_html=True)

    # Lottie Animation (Optional - wrapped in try/except)
    l_url = "https://lottie.host/8040d6c1-9031-4e76-9051-177b966b96e4/ZzQoUvV6wZ.json"
    try:
        r = requests.get(l_url, timeout=5)
        if r.status_code == 200: st_lottie(r.json(), height=200, speed=1.2)
    except: pass

    st.markdown("<h3 style='margin-top: 20px;'>SELECT BOT MODULE TO ACTIVATE:</h3>", unsafe_allow_html=True)
    
    # Grid Layout for Bot Selection
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("<div class='bot-card'><img src='https://img.icons8.com/neon/120/bot.png' width='100'/><h2>BDL</h2><p>Original</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE BDL"): 
            st.session_state.active_page = "BDL"
            st.rerun()
            
    with c2:
        st.markdown("<div class='bot-card'><img src='https://img.icons8.com/neon/120/brain.png' width='100'/><h2>THINK</h2><p>Web Scan</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE THINK"): 
            st.session_state.active_page = "Think"
            st.rerun()
            
    with c3:
        st.markdown("<div class='bot-card'><div class='dev-box'><div class='caution-tape'>DEV-ONLY</div><div style='font-size: 80px;'>🧅</div></div><h2>ONION</h2><p>Synthesis</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE ONION"):
            if is_dev: 
                st.session_state.active_page = "Onion"
                st.rerun()
            else: st.warning("Requires Dev Key.")
            
    with c4:
        st.markdown("<div class='bot-card'><div style='font-size: 80px;'>🧬</div><h2>DNA</h2><p>Genealogy</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE DNA"): 
            st.session_state.active_page = "DNA"
            st.rerun()

    # Admin Panel Section
    if is_admin:
        st.markdown("<h2 style='color:#FF8C00; border-bottom: 2px solid #FF8C00; margin-top: 50px;'>🛠️ NEXUS ADMIN COMMAND</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["📝 Q&A Requests", "📚 Cortex Training"])
        
        with t1:
            try:
                pending_qa = cortex.conn.read(worksheet="Requests", ttl="1s")
                if not pending_qa.empty:
                    st.dataframe(pending_qa, use_container_width=True)
                    qa_idx = st.number_input("Lesson ID", 0, len(pending_qa)-1, 0, key="qa_sel")
                    if st.button("✅ Approve Lesson"):
                        mem = cortex.conn.read(worksheet="Memory", ttl="1s")
                        row = pending_qa.iloc[[qa_idx]][['question', 'answer']]
                        cortex.conn.update(worksheet="Memory", data=pd.concat([mem, row], ignore_index=True))
                        cortex.conn.update(worksheet="Requests", data=pending_qa.drop(pending_qa.index[qa_idx]))
                        st.rerun()
                else: st.info("No pending Q&A lessons.")
            except: st.error("Requests Sheet Sync Error.")

        with t2:
            try:
                pending_ctx = cortex.conn.read(worksheet="ContextRequests", ttl="1s")
                if not pending_ctx.empty:
                    st.dataframe(pending_ctx, use_container_width=True)
                    ctx_idx = st.number_input("Cortex ID", 0, len(pending_ctx)-1, 0, key="ctx_sel")
                    if st.button("✅ Approve Context"):
                        core = cortex.conn.read(worksheet="Context", ttl="1s")
                        row = pending_ctx.iloc[[ctx_idx]][['Topic', 'Meaning']]
                        cortex.conn.update(worksheet="Context", data=pd.concat([core, row], ignore_index=True))
                        cortex.conn.update(worksheet="ContextRequests", data=pending_ctx.drop(pending_ctx.index[ctx_idx]))
                        st.rerun()
                else: st.info("No pending cortex blocks.")
            except: st.error("ContextRequests Sheet Sync Error.")

# Page Routing
elif page == "BDL": bot_standard.run()
elif page == "Think": bot_think.run()
elif page == "Onion": bot_onion.run()
elif page == "DNA": bot_dna.run()

# Fallback to Home if anything breaks
else:
    st.session_state.active_page = "Home"
    st.rerun()
