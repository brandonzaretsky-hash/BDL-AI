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
# These "sticky notes" keep track of the conversation flow
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
    # Attempting to link to the Master Brain Spreadsheet
    conn = st.connection("gsheets", type=GSheetsConnection)
    connection_status = "Online"
except Exception as e:
    connection_status = "Offline"
    st.error(f"Critical Connection Error: {e}")
    st.stop()

def load_brain_data():
    """Helper function to fetch the latest data with zero cache."""
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
        
    st.markdown("---")
    
    # Reset Button
    if st.button("Clear Visual History"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.write("System Status: **Encrypted**")
    st.info("Commands recognized:\n- 'forget that': Erase last memory")

#--------------------
# UI HEADER
#--------------------
st.title("🧠 BDL.AI - Master Brain")
st.caption("v2.2.1 - Enhanced Performance & Self-Learning Logic")

#--------------------
# DISPLAY CHAT HISTORY
#--------------------
# This loop renders every previous message so they don't disappear
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#--------------------
# THE MASTER BRAIN LOGIC
#--------------------
if prompt := st.chat_input("Communicate with BDL..."):
    # Immediately show the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- BLOCK 1: FORGET COMMAND ---
    # If the user made a mistake, wipe the last entry in the sheet
    if prompt.lower().strip() == "forget that":
        with st.spinner("Deleting memory from cloud..."):
            try:
                df = load_brain_data()
                if not df.empty:
                    last_q = df.iloc[-1]['question']
                    updated_df = df.drop(df.tail(1).index)
                    conn.update(data=updated_df)
                    response = f"🗑️ **Memory Wiped.** I have forgotten: '{last_q}'."
                else:
                    response = "Brain is already empty. Nothing to forget!"
            except Exception as e:
                response = f"❌ Error during deletion: {e}"

    # --- BLOCK 2: LEARNING PHASE ---
    # This runs only if BDL just said "I don't know" in the previous turn
    elif st.session_state.waiting_for_answer:
        with st.spinner("Saving new neural connection..."):
            try:
                df = load_brain_data()
                
                # Format the new knowledge
                new_entry = pd.DataFrame([{
                    "question": st.session_state.last_question.strip().lower(),
                    "answer": prompt.strip()
                }])
                
                # Combine and sync back to Google Sheets
                updated_brain = pd.concat([df, new_entry], ignore_index=True)
                conn.update(data=updated_brain)
                
                response = f"✅ **Knowledge Secured.** Next time you ask '{st.session_state.last_question}', I will answer with that."
                
                # Reset the learning flag
                st.session_state.waiting_for_answer = False
                st.session_state.last_question = ""
            except Exception as e:
                response = f"❌ Cloud Sync Error: {e}"

    #--------------------
# BLOCK 3: RETRIEVAL PHASE (WITH SMART MATCH)
#--------------------
    else:
        try:
            from thefuzz import process, fuzz
            df = load_brain_data()
            
            # 1. Clean up the sheet data (remove empty rows)
            questions_list = df['question'].fillna('').tolist()
            
            # 2. Find the "Best Match" using Fuzzy Logic
            # This looks for the closest sentence even if there are typos
            best_match, score = process.extractOne(prompt, questions_list, scorer=fuzz.token_sort_ratio)

           #--------------------
# BLOCK 3: RETRIEVAL PHASE (WITH SMART MATCH)
#--------------------
    else:
        try:
            from thefuzz import process, fuzz
            df = load_brain_data()
            
            # 1. Clean up the sheet data (remove empty rows)
            questions_list = df['question'].fillna('').tolist()
            
            # 2. Find the "Best Match" using Fuzzy Logic
            # This looks for the closest sentence even if there are typos
            best_match, score = process.extractOne(prompt, questions_list, scorer=fuzz.token_sort_ratio)
            
            #--------------------
# BLOCK 3: RETRIEVAL PHASE (WITH SMART MATCH)
#--------------------
    else:
        try:
            from thefuzz import process, fuzz
            df = load_brain_data()
            
            # 1. Clean up the sheet data (remove empty rows)
            questions_list = df['question'].fillna('').tolist()
            
            if questions_list:
                # 2. Find the "Best Match" using Fuzzy Logic
                best_match, score = process.extractOne(prompt, questions_list, scorer=fuzz.token_sort_ratio)

                # 3. Decision Logic: If match is better than 80%, answer it.
                if score >= 80:
                    response = df[df['question'] == best_match].iloc[0]['answer']
                else:
                    response = "I do not know that yet. **What should the answer be?**"
                    st.session_state.waiting_for_answer = True
                    st.session_state.last_question = prompt
            else:
                response = "My brain is currently empty! Ask me something to teach me."
                st.session_state.waiting_for_answer = True
                st.session_state.last_question = prompt
                
        except Exception as e:
            response = f"⚠️ Smart Match Error: {e}. Check if 'thefuzz' is in requirements.txt"
#--------------------

    # --- FINAL OUTPUT ---
    # Show BDL's response and save it to history
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

#--------------------
# END OF SCRIPT
#--------------------


