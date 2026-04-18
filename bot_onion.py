import streamlit as st
import cortex
import random
import re
import google.generativeai as genai

def run_onion_background_math(prompt, depth):
    """
    SYSTEMS 1, 2, & 4: INTERNAL CORE
    This math runs every time you type, mapping your words to 
    the 10-digit zip and 12-digit sequence architecture.
    """
    words = re.findall(r'\b\w+\b', prompt)
    # System 1 & 2 Execution
    _zips = {w: "".join([str(random.randint(0, 9)) for _ in range(10)]) for w in words}
    loops = max(1, depth // 5)
    for _ in range(loops):
        _logic = [f"{str(i).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(10)])}" for i in range(len(words))]
    
    # System 4: Intent & Complexity Calibration
    return min(1.0, 0.4 + (depth * 0.05))

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Synthesis Core")
    
    # Secure API Configuration
    try:
        # Pulls from Streamlit Secrets (App Settings -> Secrets)
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        # Using 1.5-flash: High speed, direct answers
        model = genai.GenerativeModel('gemini-1.5-flash') 
    except:
        st.error("🚨 SYSTEM 3 ERROR: GEMINI_API_KEY not found in Secrets. Grid offline.")
        st.info("Go to Settings -> Secrets in Streamlit and add: GEMINI_API_KEY = 'your_key'")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Clean Chat Interface
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Communicate with the Onion..."):
        # 1. Record User Intent
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Execute Hidden Onion Systems
        current_depth = len(st.session_state.messages)
        complexity_temp = run_onion_background_math(prompt, current_depth)

        # 3. System 3 & 4: Intent Synthesis
        with st.status("🧅 Peeling Layers & Scanning Neural Nodes...", expanded=False):
            try:
                # System 4 Persona: Direct, No fluff, Proper Grammar
                persona = (
                    "You are the BDL Onion. Your base is a 4-system linguistic processor. "
                    "When asked a question, provide a direct, grammatically perfect answer. "
                    "Do not define terms or give introductions unless specifically asked. "
                    "Get straight to the point based on top-tier global data."
                )
                
                # The AI Synthesis Call
                response = model.generate_content(
                    f"{persona}\n\nQuery: {prompt}",
                    generation_config={"temperature": complexity_temp}
                )
                final_answer = response.text
            except Exception as e:
                final_answer = "System 3 Synthesis failed to bridge the data gap."

        # 4. Final Output (Clean & Human)
        with st.chat_message("assistant"):
            st.markdown(final_answer)
        
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
