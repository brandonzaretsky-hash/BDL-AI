import streamlit as st
import cortex
import random, re
import google.generativeai as genai

# YOUR API KEY
API_KEY = "AIzaSyAV9aWeySnQg4P253EOk2Cu0VVFLEL5F-M"

def run_onion_math(prompt, depth):
    # System 1 & 2: Background math execution
    words = re.findall(r'\b\w+\b', prompt)
    _zips = {w: "".join([str(random.randint(0, 9)) for _ in range(10)]) for w in words}
    loops = max(1, depth // 5)
    for _ in range(loops):
        _logic = [f"{str(i).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(10)])}" for i in range(len(words))]
    return min(1.0, 0.4 + (depth * 0.05))

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Neural Bridge")

    # SYSTEM 3: CONFIGURATION
    try:
        genai.configure(api_key=API_KEY)
        # We use the standard model name here
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Configuration Error: {str(e)}")
        return

    if "onion_msgs" not in st.session_state: 
        st.session_state.onion_msgs = []

    # Display Chat
    for msg in st.session_state.onion_msgs:
        with st.chat_message(msg["role"]): 
            st.markdown(msg["content"])

    if prompt := st.chat_input("Communicate with the Onion..."):
        st.session_state.onion_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): 
            st.markdown(prompt)

        # SYSTEM 4: Complexity Logic
        temp = run_onion_math(prompt, len(st.session_state.onion_msgs))

        with st.status("🧅 Peeling layers and establishing neural bridge...", expanded=False) as status:
            try:
                # System 4 Persona Instructions
                persona = (
                    "You are the BDL Onion AI. Answer directly, using proper grammar. "
                    "Do not provide definitions or introductions. Get straight to the answer."
                )
                
                # The Request
                response = model.generate_content(
                    f"{persona}\n\nUser Question: {prompt}",
                    generation_config={"temperature": temp}
                )
                
                # Handling the response text
                answer = response.text
                status.update(label="Synthesis Complete", state="complete")
                
            except Exception as e:
                # Fallback to gemini-pro if flash is missing in your region
                try:
                    status.update(label="Rerouting to Backup Node (Gemini-Pro)...")
                    alt_model = genai.GenerativeModel('gemini-pro')
                    response = alt_model.generate_content(f"Answer directly: {prompt}")
                    answer = response.text
                    status.update(label="Synthesis Complete (Backup)", state="complete")
                except:
                    answer = f"🚨 **SYSTEM 3 BRIDGE FAILURE:** {str(e)}"
                    status.update(label="Bridge Failed", state="error")

        with st.chat_message("assistant"): 
            st.markdown(answer)
            
        st.session_state.onion_msgs.append({"role": "assistant", "content": answer})
