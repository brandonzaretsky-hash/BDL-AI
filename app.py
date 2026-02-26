import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# 1. SECURITY CHECK (Looks for password in Secrets)
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 BDL.AI - Restricted Access")
        # Pulls the password from Streamlit's hidden secrets vault
        correct_password = st.secrets["access_settings"]["password"]
        
        pw = st.text_input("Enter Access Key:", type="password")
        if st.button("Unlock Brain"):
            if pw == correct_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Unauthorized Access")
        return False
    return True

# 2. APP LOGIC (Only runs if authenticated)
if check_password():
    st.set_page_config(page_title="BDL.AI Cloud", page_icon="🧠")
    
    # Connection to Google Sheets using Secrets
    conn = st.connection("gsheets", type=GSheetsConnection)

    def load_knowledge():
        return conn.read(ttl=0)

    def save_knowledge(df):
        conn.update(data=df)

    def solve_math(text):
        if re.match(r'^[0-9\s\+\-\*\/\(\)\.]+$', text):
            try:
                return eval(text, {"__builtins__": None}, {})
            except: return None
        return None

    st.markdown('<div style="color: #28a745; font-weight: bold;">● ENCRYPTED CLOUD SESSION</div>', unsafe_allow_html=True)
    st.title("🧠 BDL.AI - Master Brain")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "learning_question" not in st.session_state:
        st.session_state.learning_question = None

    kb = load_knowledge()

    # Chat Display & Logic
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Write to BDL here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        response = ""
        # (Standard logic: Teach, Math, Search - same as before)
        if (math_result := solve_math(prompt)) is not None:
            response = f"The answer is **{math_result}**."
        else:
            # Check Knowledge Base
            clean_prompt = prompt.lower().strip()
            match = kb[kb['question'] == clean_prompt]
            if not match.empty:
                response = match.iloc[-1]['answer']
            else:
                response = "I do not know that. Please tell me the answer."
                st.session_state.learning_question = clean_prompt

        with st.chat_message("assistant"): st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
