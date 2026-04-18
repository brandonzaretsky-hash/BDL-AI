import streamlit as st
import cortex
import random, re
import google.generativeai as genai

# YOUR API KEY
API_KEY = "AIzaSyAV9aWeySnQg4P253EOk2Cu0VVFLEL5F-M"

def run_onion_math(prompt, depth):
    # System 1 & 2: Background Math
    words = re.findall(r'\b\w+\b', prompt)
    _zips = {w: "".join([str(random.randint(0, 9)) for _ in range(10)]) for w in words}
    loops = max(1, depth // 5)
    for _ in range(loops):
        _logic = [f"{str(i).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(10)])}" for i in range(len(words))]
    return min(1.0, 0.4 + (depth * 0.05))

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Diagnostic Mode")

    # Initialize API
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Failed to configure Gemini: {str(e)}")
        return

    if "onion_msgs" not in st.session_state: st.session_state.onion_msgs = []

    for msg in st.session_state.onion_msgs:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Testing Onion Connection..."):
        st.session_state.onion_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        temp = run_onion_math(prompt, len(st.session_state.onion_msgs))

        with st.status("🧅 Investigating Grid Connection...", expanded=True) as status:
            try:
                persona = "You are the BDL Onion AI. Give direct answers."
                response = model.generate_content(
                    f"{persona}\n\nQuery: {prompt}", 
                    generation_config={"temperature": temp}
                )
                answer = response.text
                status.update(label="Connection Stable", state="complete")
            except Exception as e:
                # THIS IS THE IMPORTANT PART: It will show us the REAL error
                answer = f"🚨 **SYSTEM 3 CRITICAL ERROR:** {str(e)}"
                status.update(label="Connection Failed", state="error")

        with st.chat_message("assistant"): st.markdown(answer)
        st.session_state.onion_msgs.append({"role": "assistant", "content": answer})
