import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="BDL.AI - Master Brain",
    page_icon="🧠",
    layout="centered"
)

# --- 2. CUSTOM CSS (To keep that "Master Brain" Look) ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    h1 {
        color: #00d4ff;
        text-align: center;
        text-shadow: 0 0 10px #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True) # FIXED: Changed from unsafe_allow_name_container

# --- 3. INITIALIZE SESSION STATE ---
if "waiting_for_answer" not in st.session_state:
    st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. GOOGLE SHEETS CONNECTION ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

def load_brain():
    """Reads the live Google Sheet."""
    return conn.read(ttl=0)

# --- 5. SIDEBAR (Utilities) ---
with st.sidebar:
    st.title("⚙️ Brain Settings")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.write("Current Session: **Encrypted Cloud**")
    st.info("BDL learns automatically. If it doesn't know an answer, tell it the answer in the next message.")

# --- 6. HEADER ---
st.title("🧠 BDL.AI - Master Brain")
st.caption("v2.0 - Self-Learning Neural Network via Google Sheets")

# --- 7. DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 8. THE BRAIN LOGIC ---
if prompt := st.chat_input("Write to BDL here..."):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # A. THE LEARNING PHASE
    if st.session_state.waiting_for_answer:
        with st.spinner("Writing to Cloud..."):
            try:
                # Get existing data
                df = load_brain()
                
                # Prepare the new entry
                new_row = pd.DataFrame([{
                    "question": st.session_state.last_question.strip().lower(),
                    "answer": prompt.strip()
                }])
                
                # Append and Update
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                
                response = f"✅ **Memory Secured.** I now know that '{st.session_state.last_question}' means: '{prompt}'."
                
                # Reset learning state
                st.session_state.waiting_for_answer = False
                st.session_state.last_question = ""
            except Exception as e:
                response = f"❌ **Cloud Error:** I couldn't save that. Error: {e}"

    # B. THE RETRIEVAL PHASE
    else:
        try:
            df = load_brain()
            
            # Search the 'question' column for a match
            # We use .fillna('') to prevent crashes on empty cells
            match = df[df['question'].fillna('').str.lower() == prompt.strip().lower()]
            
            if not match.empty:
                response = match.iloc[0]['answer']
            else:
                response = "I do not know that yet. **What should the answer be?** (The next thing you type will be saved as the official answer)."
                st.session_state.waiting_for_answer = True
                st.session_state.last_question = prompt
        except Exception as e:
            response = "Error accessing the Brain. Make sure your Google Sheet columns are named 'question' and 'answer'."

    # Add assistant response to UI
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
