import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="BDL.AI - Master Brain", page_icon="🧠")

st.title("🧠 BDL.AI - Master Brain")
st.markdown("---")

# --- 2. CLOUD CONNECTION ---
# This looks for your 'Digital Key' in the Streamlit Secrets box
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Connection Error: Check your Streamlit Secrets.")
    st.stop()

# --- 3. LOAD MEMORY ---
# 'ttl=0' means it always checks the cloud for new answers immediately
try:
    kb = conn.read(ttl="0s")
except Exception as e:
    st.error(f"Memory Error: I can't read the Google Sheet. {e}")
    st.stop()

# --- 4. CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
prompt = st.chat_input("Write to BDL here...")

if prompt:
    # 1. Show the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. TEACH COMMAND LOGIC
    # If the user starts a sentence with 'teach '
    if prompt.lower().startswith("teach "):
        parts = prompt.split(" ", 2)
        
        if len(parts) == 3:
            question_word = parts[1].lower().strip()
            answer_text = parts[2].strip()
            
            try:
                # Prepare the new row
                new_row = pd.DataFrame([{"question": question_word, "answer": answer_text}])
                
                # Send to Google Sheets
                conn.create(data=new_row)
                
                # Success Response
                reply = f"Cloud updated! I've recorded that '{question_word}' means: {answer_text}"
                with st.chat_message("assistant"):
                    st.success(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                # Clear cache so it remembers the new word right now
                st.cache_data.clear()
                
            except Exception as e:
                st.error(f"Could not save to Cloud: {e}")
        else:
            error_msg = "To teach me, use: teach [word] [answer]"
            with st.chat_message("assistant"):
                st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # 3. REGULAR CHAT LOGIC
    else:
        clean_prompt = prompt.lower().strip()
        
        # Check if the column 'question' exists in the sheet
        if 'question' in kb.columns:
            # Find a row where the question matches the prompt
            match = kb[kb['question'].astype(str).str.lower() == clean_prompt]
            
            if not match.empty:
                # Get the answer from the first matching row
                response = match.iloc[0]['answer']
            else:
                response = "I do not know that yet. Please tell me the answer using: teach [word] [answer]"
        else:
            response = "Error: I can't find the 'question' column in my Brain (Google Sheet)."

        # Display and save BDL's response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
