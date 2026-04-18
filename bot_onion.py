import streamlit as st
import cortex
import random, re
from fuzzywuzzy import fuzz, process

def run_onion_math(prompt, depth):
    words = re.findall(r'\b\w+\b', prompt)
    _zips = {w: "".join([str(random.randint(0, 9)) for _ in range(10)]) for w in words}
    loops = max(1, depth // 5)
    for _ in range(loops):
        _seq = [f"{str(i).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(10)])}" for i in range(len(words))]
    return True

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Synthesis")

    # DEV-ONLY SIDEBAR (Visible if qwerty)
    if st.session_state.get('is_dev', False):
        with st.sidebar:
            st.markdown("---")
            st.subheader("🛠️ ONION DEV BAR")
            if st.button("📊 View Brain Map (Approved)"):
                df = cortex.conn.read(worksheet="Context", ttl="1s")
                st.dataframe(df[df['Status'] == 'Approved'])

    if "onion_msgs" not in st.session_state: st.session_state.onion_msgs = []
    for msg in st.session_state.onion_msgs:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Query the synthesized nodes..."):
        st.session_state.onion_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        run_onion_math(prompt, len(st.session_state.onion_msgs))

        with st.status("🧅 Peeling Layers...", expanded=False):
            try:
                all_df = cortex.conn.read(worksheet="Context", ttl="1s")
                ctx_df = all_df[all_df['Status'] == 'Approved']
                topics = ctx_df['Topic'].fillna('').tolist()
                match, score = process.extractOne(prompt, topics, scorer=fuzz.token_set_ratio)
                
                if score >= 70:
                    ans = ctx_df[ctx_df['Topic'] == match].iloc[-1]['Meaning']
                else:
                    ans = "System 3: Topic unapproved or unknown. Run THINK mode to scout it."
            except:
                ans = "🚨 Connection Failure."

        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.onion_msgs.append({"role": "assistant", "content": ans})
