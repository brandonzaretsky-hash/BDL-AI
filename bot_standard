import streamlit as st
import cortex
from deep_translator import GoogleTranslator
from fuzzywuzzy import fuzz, process

def run():
    cortex.apply_theme("standard")
    st.title("🤖 BDL Standard")
    
    with st.sidebar:
        lang_map = {"None": "none", "Hebrew": "iw", "French": "fr", "Japanese": "ja"}
        choice = st.selectbox("Language", list(lang_map.keys()))
        voice_on = st.toggle("Voice", True)

    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask BDL..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        df = cortex.conn.read(worksheet="Memory", ttl="1s")
        qs = df['question'].fillna('').tolist()
        match, score = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
        response = df[df['question'] == match].iloc[-1]['answer'] if score >= 85 else "I don't know that yet."
        
        trans = GoogleTranslator(source='auto', target=lang_map[choice]).translate(response) if choice != "None" else None
        full = f"{response}\n\n----- \n {trans}" if trans else response
        
        with st.chat_message("assistant"):
            st.markdown(full)
            if voice_on: cortex.show_voices(response, trans, lang_map[choice], choice)
        st.session_state.messages.append({"role": "assistant", "content": full})
