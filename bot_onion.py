import streamlit as st
import cortex
import random
import re
import google.generativeai as genai

def run_onion_background_math(prompt, depth):
    """
    SYSTEMS 1, 2, & 4: THE ARCHITECTURE
    This simulates how an AI 'thinks' using your zip-code and sequencing bases.
    """
    words = re.findall(r'\b\w+\b', prompt)
    # System 1: Zip Mapping (Simulating Tokenization)
    _zips = {w: "".join([str(random.randint(0, 9)) for _ in range(10)]) for w in words}
    
    # System 4: Controller Decision
    # High history depth = Higher 'Temperature' (more creative)
    calc_temp = min(1.0, 0.3 + (depth * 0.1))
    
    # System 2: Sequence Looping
    # Simulating the 'Attention' layers of an AI
    loops = max(1, depth // 5)
    for _ in range(loops):
        _logic = [f"{str(i).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(10)])}" for i in range(len(words))]
    
    return calc_temp

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: AI Neural Core")
    st.caption("SYSTEM 1-4 INTEGRATED | GENERATIVE SYNTHESIS ACTIVE")

    # Access the API Key from Secrets
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # The 'less powerful' but fast version
    except:
        st.error("🚨 SYSTEM 3 FAILURE: API Key missing in Secrets. Please add GEMINI_API_KEY.")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Talk to the Onion..."):
        # 1. User Input
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Run Background Systems
        current_depth = len(st.session_state.messages)
        ai_temp = run_onion_background_math(prompt, current_depth)

        # 3. System 3 & 4: Generative Synthesis
        with st.status("🧅 Peeling Layers & Scanning Neural Nodes...", expanded=True) as status:
            st.write("System 1: Generating 10-digit word blocks...")
            st.write("System 2: Sequencing 12-digit attention matrix...")
            st.write(f"System 4: Calibrating response temperature to {ai_temp}...")

            try:
                # We feed the AI the 'Onion' persona instructions
                instruction = (
                    "You are the BDL Onion AI. Answer directly and grammatically. "
                    "Do not give definitions unless asked. Get straight to the answer. "
                    "Base your tone on a sophisticated synthesis engine."
                )
                
                # The actual AI call
                response = model.generate_content(
                    f"{instruction}\n\nUser Question: {prompt}",
                    generation_config=genai.types.GenerationConfig(
                        temperature=ai_temp,
                        max_output_tokens=500
                    )
                )
                final_answer = response.text
            except Exception as e:
                final_answer = f"System 3 Synthesis Error: {str(e)}"

            status.update(label="Synthesis Complete", state="complete")

        # 4. Final Output
        with st.chat_message("assistant"):
            st.markdown(final_answer)
        
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
