import streamlit as st
import cortex # Import the brain
from deep_translator import GoogleTranslator
from fuzzywuzzy import fuzz, process

def run():
    cortex.apply_theme("standard")
    st.title("🤖 BDL Standard")
    
    with st.sidebar:
        # We use lowercase codes for the gTTS engine
        lang_map = {"None": "none", "Hebrew": "iw", "French": "fr", "Japanese": "ja", "Spanish": "es"}
        choice = st.selectbox("Select Matrix Language", list(lang_map.keys()))
        voice_on = st.toggle("Activate Voice Output", True)

    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Communicate..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        response = ""
        try:
            df = cortex.conn.read(worksheet="Memory", ttl="1s")
            qs = df['question'].fillna('').tolist()
            match, score = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
            if score >= 85: 
                response = df[df['question'] == match].iloc[-1]['answer']
        except: pass
        
        if not response: response = "I haven't learned that lesson yet."
        
        # Translation Logic
        trans = None
        if choice != "None":
            try:
                trans = GoogleTranslator(source='auto', target=lang_map[choice]).translate(response)
            except: trans = "[Translation Error]"

        full = f"{response}\n\n---\n**Translation:** {trans}" if trans else response
        
        with st.chat_message("assistant"):
            st.markdown(full)
            # THE LINE 32 CALL:
            if voice_on: 
                cortex.show_voices(response, trans, lang_map[choice], choice)
        
        st.session_state.messages.append({"role": "assistant", "content": full})
