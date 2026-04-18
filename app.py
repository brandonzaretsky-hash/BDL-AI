import streamlit as st
import cortex, bot_standard, bot_think, bot_onion, bot_dna
import pandas as pd

st.set_page_config(page_title="BDL.AI NEXUS", layout="wide")
cortex.apply_theme("cyberpunk")

if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

with st.sidebar:
    st.title("🔑 Access Panel")
    if st.button("🌐 RETURN HOME"): 
        st.session_state.active_page = "Home"; st.rerun()
    
    key = st.text_input("Credentials", type="password")
    st.session_state.is_dev = (key == "qwerty")
    st.session_state.is_admin = (key in ["admin", "qwerty"])

    # MODERATION DECK (Approve/Decline)
    if st.session_state.is_admin:
        st.markdown("---")
        st.subheader("🛡️ Moderation Deck")
        try:
            df = cortex.conn.read(worksheet="Context", ttl="1s")
            pending = df[df['Status'] == 'Pending']
            if not pending.empty:
                item = pending.iloc[0]
                st.info(f"**Topic:** {item['Topic']}\n**Data:** {item['Meaning']}")
                c1, c2 = st.columns(2)
                if c1.button("✅ Approve"):
                    df.loc[df['Topic'] == item['Topic'], 'Status'] = 'Approved'
                    cortex.conn.update(worksheet="Context", data=df)
                    st.rerun()
                if c2.button("❌ Decline"):
                    df = df[df['Topic'] != item['Topic']]
                    cortex.conn.update(worksheet="Context", data=df)
                    st.rerun()
            else: st.write("No pending nodes.")
        except: st.write("GSheet Error.")

page = st.session_state.active_page
if page == "Home":
    st.markdown("<h1>BDL.AI NEXUS</h1>", unsafe_allow_html=True)
    score = cortex.get_total_intelligence()
    st.markdown(f"<div style='text-align:center;font-size:30px;border:1px solid #00ff41;'>{score} APPROVED NODES</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🤖 BDL STANDARD"): st.session_state.active_page = "BDL"; st.rerun()
    with col2:
        if st.button("🧠 BDL THINK"): st.session_state.active_page = "Think"; st.rerun()
    with col3:
        if st.button("🧅 BDL ONION"):
            if st.session_state.is_dev: st.session_state.active_page = "Onion"; st.rerun()
            else: st.warning("Dev Access Required.")

elif page == "BDL": bot_standard.run()
elif page == "Think": bot_think.run()
elif page == "Onion": bot_onion.run()
