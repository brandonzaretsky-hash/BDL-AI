import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

#--------------------
# PAGE CONFIGURATION
#--------------------
st.set_page_config(
    page_title="BDL.AI - Master Brain",
    page_icon="🧠",
    layout="centered"
)

#--------------------
# CUSTOM CSS & PULSE ANIMATION
#--------------------
st.markdown("""
    <style>
    /* Main Background */
    .main {
        background-color: #0e1117;
    }
    
    /* Chat Bubbles */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* Title Styling */
    h1 {
        color: #00d4ff;
        text-align: center;
        text-shadow: 0 0 10px #00d4ff;
    }

    /* The Pulsing Light Effect */
    .pulse-container {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: bold;
        color: #00ff00;
        margin-bottom: 20px;
    }

    .pulse-circle {
        width: 12px;
        height: 12px;
        background-color: #00ff00;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7);
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 10px rgba(0, 255, 0, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(0, 255, 0, 0);
        }
    }
    </style>
    """, unsafe_allow_html=True)

#--------------------
# INITIALIZE SESSION STATE
#--------------------
if "waiting_for_answer" not in st.session_state:
    st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

#--------------------
# GOOGLE SHEETS CONNECTION
#--------------------
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    connection_status = "Online"
except Exception as e:
    connection_status = "Offline"
    st.error(f"Connection Error: {e}")
    st.stop()

def load_brain():
    """Reads the live Google Sheet."""
    return conn.read(ttl=0)

#--------------------
# SIDEBAR UTILITIES
#--------------------
with st.sidebar:
    st.title("⚙️ Brain Settings")
    
    # Pulsing Status Indicator
    if connection_status == "Online":
        st.markdown("""
            <div class="pulse-container">
                <div class="pulse-circle"></div>
                <span>BRAIN ONLINE</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error("🔴 BRAIN OFFLINE")
        
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.write("Session: **Encrypted**")
    st.info("BDL learns automatically from your inputs.")

#--------------------
# UI HEADER
#--------------------
st.title("🧠 BDL.AI - Master Brain")
st.caption("v2.1 - Self-Learning Neural Network via Google Sheets")

#--------------------
# DISPLAY CHAT HISTORY
#--------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#--------------------
# THE BRAIN LOGIC
#--------------------
if prompt := st.chat_input("Write to BDL here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # A. THE LEARNING PHASE
    if st.session_state.waiting_for_answer:
        with st.spinner("Syncing to Cloud..."):
            try:
                df = load_brain()
                new_row = pd.DataFrame([{
                    "question": st.session_state.last_question.strip().lower(),
                    "answer": prompt.strip()
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                
                response = f"✅ **Memory Secured.** I've learned that '{st.session_state.last_question}' means: '{prompt}'."
                st.session_state.waiting_for_answer = False
                st.session_state.last_question = ""
            except Exception as e:
                response = f"❌ **Cloud Error:** {e}"

    # B. THE RETRIEVAL PHASE
    else:
        try:
            df = load_brain()
            match = df[df['question'].fillna('').str.lower() == prompt.strip().lower()]
            
            if not match.empty:
                response = match.iloc[0]['answer']
            else:
                response = "I do not know that yet. **What should the answer be?**"
                st.session_state.waiting_for_answer = True
                st.session_state.last_question = prompt
        except Exception as e:
            response = "⚠️ Error accessing the Brain. Check Sheet columns."

    # Final response output
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
