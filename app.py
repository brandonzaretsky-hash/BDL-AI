import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="BDL.AI - Master Brain", page_icon="🧠")

# --- 2. PASSWORD PROTECTION ---
# This looks for the password you set in Streamlit Secrets
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.title("🔐 BDL.AI - Encrypted Session")
    password_input = st.text_input("Enter Brain Access Code:", type="password")
    
    # This pulls 'password' from your [access_settings] in Secrets
    if password_input == st.secrets["access_settings"]["password"]:
        st.session_state.password_correct = True
        st.rerun()
    elif password_input:
        st.error("❌ Access Denied: Incorrect Password")
    return False

if not check_password():
    st.stop()

# --- 3. CLOUD CONNECTION & LOAD ---
st.title("🧠 BDL.AI - Master Brain")
st.write("● ENCRYPTED CLOUD SESSION ACTIVE")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    kb = conn.read(ttl="0s")
except Exception as e:
    st.error(f"⚠️ Brain Connection Error: {e}")
    st.stop()

# --- 4. MATH ENGINE ---
def solve_math(text):
    # This looks for numbers and symbols like +, -, *, /
    clean_text = text.replace("x", "*").replace("÷", "/")
    equation = re.findall(r'[0-9+\-*/(). ]+', clean_text)
    if equation:
        try:
            result = eval(equation[0])
            return f"The answer is {result}"
        except:
            return None
    return None

# --- 5. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Write to BDL here...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # A. TEACH COMMAND
    if prompt.lower().startswith("teach "):
        parts = prompt.split(" ", 2)
        if len(parts) == 3:
            q_to_save = parts[1].lower().strip()
            a_to_save = parts[2].strip()
            try:
                new_row = pd.DataFrame([{"question": q_to_save, "answer": a_to_save}])
                conn.create(data=new_row)
                response = f"✅ Cloud updated! I've recorded that '{q_to_save}' means: {a_to_save}"
                st.cache_data.clear()
            except Exception as e:
                response = f"❌ Error saving to Cloud: {e}"
        else:
            response = "⚠️ Use format: teach [word] [answer]"

    # B. MATH CHECK
    elif any(char.isdigit() for char in prompt) and any(op in prompt for op in "+-*/"):
        math_result = solve_math(prompt)
        response = math_result if math_result else "I see numbers, but I can't solve that equation yet."

    # C. MEMORY CHECK (Google Sheets)
    else:
        clean_prompt = prompt.lower().strip()
        if not kb.empty and 'question' in kb.columns:
            match = kb[kb['question'].astype(str).str.lower() == clean_prompt]
            if not match.empty:
                response = match.iloc[0]['answer']
            else:
                response = "I do not know that. Please tell me the answer using the 'teach' command."
        else:
            response = "⚠️ Error: Memory columns ('question', 'answer') missing from Row 1 of Google Sheet."

    # Final Response Delivery
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
