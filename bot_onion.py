import streamlit as st
import cortex
import random, re
from fuzzywuzzy import fuzz, process

def run_onion_math(prompt, depth):
    """Background System 1, 2, and 4 logic."""
    words = re.findall(r'\b\w+\b', prompt)
    # System 1: Zip Mapping
    _zips = {w: "".join([str(random.randint(0, 9)) for _ in range(10)]) for w in words}
    # System 2: Sequencing
    loops = max(1, depth // 5)
    for _ in range(loops):
        _logic = [f"{str(i).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(10)])}" for i in range(len(words))]
    return True

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Synthesis")

    if "onion_msgs" not in st.session_state: 
        st.session_state.onion_msgs = []

    for msg in st.session_state.onion_msgs:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Query the Onion..."):
        st.session_state.onion_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # Run Hidden Systems
        run_onion_math(prompt, len(st.session_state.onion_msgs))

        with st.status("🧅 Peeling Layers...", expanded=False) as status:
            try:
                # System 3: Synthesis from Context Sheet
                ctx_df = cortex.conn.read(worksheet="Context", ttl="1s")
                topics = ctx_df['Topic'].fillna('').tolist()
                match, score = process.extractOne(prompt, topics, scorer=fuzz.token_set_ratio)
                
                if score >= 75:
                    ans = ctx_df[ctx_df['Topic'] == match].iloc[-1]['Meaning']
                else:
                    ans = "System 3: No stable data node found. Refine your query or update the Cortex."
                
                status.update(label="Synthesis Complete", state="complete")
            except:
                ans = "🚨 System 3: GSheet Link Broken."
                status.update(label="Bridge Failed", state="error")

        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.onion_msgs.append({"role": "assistant", "content": ans})
