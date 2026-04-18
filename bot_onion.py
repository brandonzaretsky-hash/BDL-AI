import streamlit as st
import cortex
import random, re
import google.generativeai as genai

# YOUR ACTIVE API KEY
API_KEY = "AIzaSyAV9aWeySnQg4P253EOk2Cu0VVFLEL5F-M"

def run_onion_math(prompt, depth):
    """SYSTEMS 1, 2, & 4: BACKGROUND ARCHITECTURE"""
    words = re.findall(r'\b\w+\b', prompt)
    # System 1: Zip Mapping
    _zips = {w: "".join([str(random.randint(0, 9)) for _ in range(10)]) for w in words}
    # System 4: Complexity scaling based on chat depth
    loops = max(1, depth // 5)
    for _ in range(loops):
        # System 2: 12-digit sequencing
        _logic = [f"{str(i).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(10)])}" for i in range(len(words))]
    return min(1.0, 0.4 + (depth * 0.05))

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Stable Neural Bridge")

    # SYSTEM 3: CONFIGURATION & MODEL SELECTION
    if "onion_msgs" not in st.session_state: 
        st.session_state.onion_msgs = []

    # Display Chat History
    for msg in st.session_state.onion_msgs:
        with st.chat_message(msg["role"]): 
            st.markdown(msg["content"])

    if prompt := st.chat_input("Communicate with the Onion..."):
        st.session_state.onion_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): 
            st.markdown(prompt)

        # Run background logic
        temp = run_onion_math(prompt, len(st.session_state.onion_msgs))

        with st.status("🧅 Peeling layers and establishing stable neural bridge...", expanded=False) as status:
            final_answer = ""
            # Establish the persona for System 4
            persona = (
                "You are the BDL Onion AI. Answer directly using proper grammar. "
                "Do not provide definitions, introductions, or 'Here is the answer'. "
                "Get straight to the data synthesis based on the user's intent."
            )
            
            try:
                # Configuration
                genai.configure(api_key=API_KEY)
                
                # ATTEMPT 1: Modern Stable Flash
                try:
                    status.update(label="Scanning Neural Node: 1.5-Flash...")
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"{persona}\n\nQuery: {prompt}")
                    final_answer = response.text
                except:
                    # ATTEMPT 2: Legacy Stable naming
                    status.update(label="Node 1.5-Flash Offline. Rerouting to 1.0-Pro...")
                    model = genai.GenerativeModel('gemini-1.0-pro')
                    response = model.generate_content(f"{persona}\n\nQuery: {prompt}")
                    final_answer = response.text
                
                status.update(label="Synthesis Complete", state="complete")
                
            except Exception as e:
                # System 3 Final Fallback
                final_answer = f"🚨 **SYSTEM 3 CRITICAL ERROR:** All nodes failed. Trace: {str(e)}"
                status.update(label="Bridge Failed", state="error")

        with st.chat_message("assistant"): 
            st.markdown(final_answer)
            
        st.session_state.onion_msgs.append({"role": "assistant", "content": final_answer})
