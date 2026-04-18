import streamlit as st
from utils import conn, apply_theme, show_voices
from deep_translator import GoogleTranslator
from fuzzywuzzy import fuzz, process

apply_theme("standard")
st.title("🤖 BDL Standard")

if "messages" not in st.session_state: st.session_state.messages = []

# Sidebar Language Controls
lang_map = {"None": "none", "Hebrew": "iw", "French": "fr", "Japanese": "ja"}
choice = st.sidebar.selectbox("Language", list(lang_map.keys()))
voice_on = st.sidebar.toggle("Voice", True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Communicate..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    df = conn.read(worksheet="Memory", ttl="1s")
    qs = df['question'].fillna('').tolist()
    match, score = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
    response = df[df['question'] == match].iloc[-1]['answer'] if score >= 85 else "I don't know that yet."
    
    trans = GoogleTranslator(source='auto', target=lang_map[choice]).translate(response) if choice != "None" else None
    full = f"{response}\n\n----- \n {trans}" if trans else response
    
    with st.chat_message("assistant"):
        st.markdown(full)
        if voice_on: show_voices(response, trans, lang_map[choice], choice)
    st.session_state.messages.append({"role": "assistant", "content": full})
