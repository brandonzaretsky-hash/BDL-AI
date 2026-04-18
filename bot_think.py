import streamlit as st
import cortex, wikipedia, wikipediaapi

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧠 BDL Think")
    sport = st.sidebar.toggle("Sport Mode")
    strict = st.sidebar.slider("Strictness", 50, 100, 85)
    
    prompt = st.chat_input("Web scan topic...")
    if prompt:
        with st.status("Accessing Grid..."):
            wiki = wikipediaapi.Wikipedia(user_agent='BDL-AI/1.0', language='en')
            search = wikipedia.search(prompt)
            res = wiki.page(search[0]).text[:5000] if search else "No records found."
            if sport and search: res = wiki.page(search[0]).summary
        st.markdown(f"### 🔍 RESULTS\n\n{res}")
