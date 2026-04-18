import streamlit as st
import cortex
import random, re
import google.generativeai as genai

def run_onion_math(prompt, depth):
    """SYSTEMS 1, 2, & 4: BACKGROUND ARCHITECTURE"""
    words = re.findall(r'\b\w+\b', prompt)
    _zips = {w: "".join([str(random.randint(0, 9)) for _ in range(10)]) for w in words}
    loops = max(1, depth // 5)
    for _ in range(loops):
        _logic = [f"{str(i).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(10)])}" for i in range(len(words))]
    return min(1.0, 0.4 + (depth * 0.05))

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Universal Node")

    # SYSTEM 3: CONFIGURATION
    try:
        # PULLING FROM SECRETS (REQUIRED FOR SAFETY)
        API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=API_KEY)
    except Exception as e:
        st.error("🚨 KEY ERROR: No 'GEMINI_API_KEY' found in Streamlit Secrets.")
        st.info("1. Go to Google AI Studio and get a NEW key.\n2. In Streamlit Cloud, go to Settings -> Secrets.\n3. Add: GEMINI_API_KEY = 'your_key'")
        return

    if "onion_msgs" not in st.session_state: 
        st.session_state.onion_msgs = []

    for msg in st.session_state.onion_msgs:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Testing Universal Connection..."):
        st.session_state.onion_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        temp = run_onion_math(prompt, len(st.session_state.onion_msgs))

        with st.status("🧅 Scanning for available neural nodes...", expanded=True) as status:
            final_answer = ""
            # The list of models we will hunt for
            model_nodes = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro', 'gemini-pro']
            
            connected = False
            for node in model_nodes:
                if connected: break
                try:
                    status.update(label=f"Attempting Bridge: {node}...")
                    model = genai.GenerativeModel(node)
                    
                    persona = "You are the BDL Onion. Answer directly and grammatically. No intro/outro."
                    response = model.generate_content(f"{persona}\n\nQuery: {prompt}")
                    
                    final_answer = response.text
                    connected = True
                    status.update(label=f"Connection Secured: {node}", state="complete")
                except Exception as e:
                    status.update(label=f"Node {node} rejected connection.")
                    continue

            if not connected:
                final_answer = "🚨 **SYSTEM 3 TOTAL BLACKOUT:** All neural nodes rejected the API key. The key may be revoked or inactive."
                status.update(label="All Bridges Failed", state="error")

        with st.chat_message("assistant"): 
            st.markdown(final_answer)
            
        st.session_state.onion_msgs.append({"role": "assistant", "content": final_answer})
