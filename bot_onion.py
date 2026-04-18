import streamlit as st
import cortex
import random, re
from fuzzywuzzy import fuzz, process

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion")

    if "onion_msgs" not in st.session_state: st.session_state.onion_msgs = []
    for msg in st.session_state.onion_msgs:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Query..."):
        st.session_state.onion_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.status("🧅 Peeling..."):
            try:
                all_df = cortex.conn.read(worksheet="Context", ttl="1s")
                # ONLY USE APPROVED DATA
                ctx_df = all_df[all_df['Status'] == 'Approved']
                
                topics = ctx_df['Topic'].fillna('').tolist()
                match, score = process.extractOne(prompt, topics, scorer=fuzz.token_set_ratio)
                
                if score >= 70:
                    ans = ctx_df[ctx_df['Topic'] == match].iloc[-1]['Meaning']
                else:
                    ans = "System 3: No approved node found. Search in THINK mode to scout this."
            except:
                ans = "🚨 Connection Error."

        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.onion_msgs.append({"role": "assistant", "content": ans})
