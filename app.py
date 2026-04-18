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
    is_dev = (key == "qwerty")
    is_admin = (key in ["admin", "qwerty"])

    # RESTORED MODERATION DECK
    if is_admin:
        st.markdown("---")
        st.subheader("🛡️ Moderation Deck")
        try:
            df = cortex.conn.read(worksheet="Context", ttl="1s")
            pending = df[df['Status'] == 'Pending']
            if not pending.empty:
                item = pending.iloc[0]
                st.info(f"**Topic:** {item['Topic']}\n\n**Data:** {item['Meaning']}")
                c1, c2 = st.columns(2)
                if c1.button("✅ Approve"):
                    df.loc[df['Topic'] == item['Topic'], 'Status'] = 'Approved'
                    cortex.conn.update(worksheet="Context", data=df)
                    st.rerun()
                if c2.button("❌ Decline"):
                    df = df[df['Topic'] != item['Topic']]
                    cortex.conn.update(worksheet="Context", data=df)
                    st.rerun()
            else: st.write("✅ Cortex is clean.")
        except: st.write("GSheet Error.")

page = st.session_state.active_page

if page == "Home":
    st.markdown("<h1>BDL.AI NEXUS GATEWAY</h1>", unsafe_allow_html=True)
    score = cortex.get_total_intelligence()
    st.markdown(f"<div class='intel-counter'><span>{score}</span><br><small>DATA NODES IN CORTEX</small></div>", unsafe_allow_html=True)

    # RESTORED 4-COLUMN CARD UI
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='bot-card'><h2>🤖</h2><h3>BDL</h3><p>Standard</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE BDL"): st.session_state.active_page = "BDL"; st.rerun()
    with c2:
        st.markdown("<div class='bot-card'><h2>🧠</h2><h3>THINK</h3><p>Auto-Scout</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE THINK"): st.session_state.active_page = "Think"; st.rerun()
    with c3:
        st.markdown("<div class='bot-card'><h2>🧅</h2><h3>ONION</h3><p>Synthesis</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE ONION"):
            if is_dev: st.session_state.active_page = "Onion"; st.rerun()
            else: st.warning("Dev Access Required.")
    with c4:
        st.markdown("<div class='bot-card'><h2>🧬</h2><h3>DNA</h3><p>Genealogy</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE DNA"): st.session_state.active_page = "DNA"; st.rerun()

elif page == "BDL": bot_standard.run()
elif page == "Think": bot_think.run()
elif page == "Onion": bot_onion.run()
elif page == "DNA": bot_dna.run()
