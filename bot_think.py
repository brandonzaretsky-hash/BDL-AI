import streamlit as st
import cortex
import wikipedia, wikipediaapi

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧠 BDL Think")
    sport = st.sidebar.toggle("Sport Mode")
    
    prompt = st.chat_input("Deep scan topic...")
    if prompt:
        with st.status("Scanning Grid..."):
            wiki = wikipediaapi.Wikipedia(user_agent='BDL-AI/1.0', language='en')
            search = wikipedia.search(prompt)
            res = wiki.page(search[0]).summary if search else "No records."
        st.markdown(res)
