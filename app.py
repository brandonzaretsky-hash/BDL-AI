import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

# ==========================================
# 1. SECURITY SETTINGS
# ==========================================
# CHANGE THIS TO WHATEVER YOU WANT YOUR PASSWORD TO BE!
BDL_PASSWORD = "244466666" 

def check_password():
    """Returns True if the user had the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 BDL.AI - System Locked")
        pw = st.text_input("Enter Access Key:", type="password")
        if st.button("Unlock Brain"):
            if pw == BDL_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Access Denied. Incorrect Key.")
        return False
    return True

# ==========================================
# 2. THE REST OF YOUR BDL CODE
# ==========================================

# Only run the app if the password is correct
if check_password():
    # Put all your existing code inside this block!
    
    # (I'll re-include the main parts so you can copy/paste the whole thing)
    MEMORY_FILE = "qa_memory.csv"

    def load_knowledge():
        if not os.path.exists(MEMORY_FILE):
            return pd.DataFrame(columns=["question", "answer"])
        return pd.read_csv(MEMORY_FILE)

    def save_knowledge(df):
        df.to_csv(MEMORY_FILE, index=False)

    def solve_math(text):
        if re.match(r'^[0-9\s\+\-\*\/\(\)\.]+$', text):
            try:
                return eval(text, {"__builtins__": None}, {})
            except:
                return None
        return None

    st.set_page_config(page_title="BDL.AI", page_icon="🧠")

    st.markdown("""
        <div style="background-color: #f8d7da; padding: 10px; border-radius: 5px; border: 1px solid #f5c6cb; margin-bottom: 20px; display: flex; align-items: center;">
            <span style="color: #721c24; font-weight: bold; margin-right: 10px;">● SECURE SESSION ACTIVE</span>
        </div>
    """, unsafe_allow_html=True)

    st.title("🧠 BDL.AI - Master Brain")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "learning_question" not in st.session_state:
        st.session_state.learning_question = None

    kb = load_knowledge()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Authorized access only..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = ""
        
        # Logout command just for fun
        if prompt.lower() == "/logout":
            st.session_state.authenticated = False
            st.rerun()

        # COMMAND: /UNDO
        elif prompt.strip().lower() == "/undo":
            if not kb.empty:
                removed = kb.iloc[-1]
                kb = kb.drop(kb.index[-1])
                save_knowledge(kb)
                response = f"⚠️ **Undo Successful.** Forgot: '{removed['question']}'."
            else:
                response = "Brain is empty."

        # LOGIC: LEARNING
        elif st.session_state.learning_question:
            new_entry = pd.DataFrame({"question": [st.session_state.learning_question], "answer": [prompt]})
            kb = pd.concat([kb, new_entry], ignore_index=True)
            save_knowledge(kb)
            response = f"Got it! Answer recorded."
            st.session_state.learning_question = None

        # LOGIC: TEACHQA
        elif prompt.lower().startswith(("teach ", "teachqa ")):
            parts = prompt.split(" ", 2) 
            if len(parts) >= 3:
                q, a = parts[1].lower().strip(), parts[2].strip()
                new_entry = pd.DataFrame({"question": [q], "answer": [a]})
                kb = pd.concat([kb, new_entry], ignore_index=True)
                save_knowledge(kb)
                response = f"Knowledge updated."
            else:
                response = "Use: `teach [question] [answer]`"

        # LOGIC: MATH
        elif (math_result := solve_math(prompt)) is not None:
            response = f"The answer is **{math_result}**."

        # LOGIC: SEARCH
        else:
            clean_prompt = prompt.lower().strip()
            match = kb[kb['question'] == clean_prompt]
            if not match.empty:
                response = match.iloc[-1]['answer']
            else:
                response = "I do not know the answer to that. Please tell me what the answer is."
                st.session_state.learning_question = clean_prompt

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})