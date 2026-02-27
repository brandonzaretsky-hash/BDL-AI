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
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    h1 { color: #00d4ff; text-align: center; text-shadow: 0 0 10px #00d4ff; }

    .pulse-container { display: flex; align-items: center; gap: 10px; font-weight: bold; color: #00ff00; margin-bottom: 20px; }
    .pulse-circle {
        width: 12px; height: 12px; background-color: #00ff00; border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
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

def load_brain_data():
    return conn.read(ttl=0)

#--------------------
# SIDEBAR UTILITIES
#--------------------
with st.sidebar:
    st.title("⚙️ Brain Settings")
    
    if connection_status == "Online":
        st.markdown('<div class="pulse-container"><div class="pulse-circle"></div><span>BRAIN ONLINE</span></div>', unsafe_allow_html=True)
    else:
        st.error("🔴 BRAIN OFFLINE")

    # NEW: The Confidence Slider
    st.markdown("---")
    st.write("🧠 **Smart Match Sensitivity**")
    confidence_level = st.sidebar.slider(
        "Higher = Stricter", 
        min_value=50, 
        max_value=100, 
        value=80,
        help="How closely your typing must match the brain's memory to get an answer."
    )
    
    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.info("Commands:\n- 'forget that': Deletes the last learned item.")

#--------------------
# UI HEADER
#--------------------
st.title("🧠 BDL.AI - Master Brain")
st.caption("v2.3 - Fuzzy Logic & Self-Correction Active")

#--------------------
# DISPLAY CHAT HISTORY
#--------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#--------------------
# THE MASTER BRAIN LOGIC
#--------------------
if prompt := st.chat_input("Communicate with BDL..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = ""

    # --- BLOCK 0: CALCULATOR MODULE (NEW) ---
    # This checks for numbers and math symbols (+, -, *, /)
    import re
    math_pattern = r"^[\d\+\-\*\/\(\)\s\.]+$"
    
    # If the input looks like math and doesn't have a stored answer yet
    if re.match(math_pattern, prompt.strip()):
        try:
            # Dangerous to use 'eval', but 'pd.eval' is safer for simple math
            result = pd.eval(prompt)
            response = f"🔢 **Calculation Result:** {result}"
        except:
            pass # If math fails, it will move to retrieval/learning

    # --- BLOCK 1: FORGET COMMAND ---
    if not response and prompt.lower().strip() == "forget that":
        with st.spinner("Erasing last neural link..."):
            try:
                df = load_brain_data()
                if not df.empty:
                    last_q = df.iloc[-1]['question']
                    updated_df = df.drop(df.tail(1).index)
                    conn.update(data=updated_df)
                    response = f"🗑️ **Memory Wiped.** I have forgotten the answer for: '{last_q}'."
                else:
                    response = "Brain is already empty!"
            except Exception as e:
                response = f"❌ Error: {e}"

    # --- BLOCK 2: LEARNING PHASE ---
    elif not response and st.session_state.waiting_for_answer:
        with st.spinner("Syncing to Cloud..."):
            try:
                df = load_brain_data()
                new_row = pd.DataFrame([{"question": st.session_state.last_question.strip().lower(), "answer": prompt.strip()}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                response = f"✅ **Memory Secured.** Learned that '{st.session_state.last_question}' means: '{prompt}'."
                st.session_state.waiting_for_answer = False
                st.session_state.last_question = ""
            except Exception as e:
                response = f"❌ Cloud Error: {e}"

    # --- BLOCK 3: RETRIEVAL PHASE (SMART MATCH) ---
    elif not response:
        try:
            from thefuzz import process, fuzz
            df = load_brain_data()
            questions_list = df['question'].fillna('').tolist()
            
            if questions_list:
                best_match, score = process.extractOne(prompt, questions_list, scorer=fuzz.token_sort_ratio)

                if score >= confidence_level:
                    response = df[df['question'] == best_match].iloc[0]['answer']
                else:
                    response = "I do not know that yet. **What should the answer be?**"
                    st.session_state.waiting_for_answer = True
                    st.session_state.last_question = prompt
            else:
                response = "My brain is empty. Teach me something!"
                st.session_state.waiting_for_answer = True
                st.session_state.last_question = prompt
        except Exception as e:
            response = "⚠️ Brain Access Error. Check your Sheet columns."

   
#--------------------
# END OF SCRIPT
#--------------------

    # Final response output
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


