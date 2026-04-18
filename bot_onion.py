import streamlit as st
import cortex, re
from fuzzywuzzy import fuzz, process

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion")
    prompt = st.chat_input("Peel context...")
    if prompt:
        with st.status("Analyzing layers..."):
            ctx_df = cortex.conn.read(worksheet="Context", ttl="1s")
            match, score = process.extractOne(prompt, ctx_df['Topic'].tolist(), scorer=fuzz.token_set_ratio)
            res = ctx_df[ctx_df['Topic'] == match].iloc[-1]['Meaning'] if score >= 80 else "No context found."
        st.markdown(f"### 🧪 SYNTHESIS\n\n{res}")
