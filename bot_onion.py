import streamlit as st
import cortex
import random, re
from fuzzywuzzy import fuzz, process

def run_onion_math(prompt, depth):
    """
    INTERNAL CORE: SYSTEMS 1, 2, & 4
    Executes the 10-digit Zip and 12-digit Sequence math in the background.
    """
    words = re.findall(r'\b\w+\b', prompt)
    # System 1: Zip Mapping (10-digit)
    _zips = {w: "".join([str(random.randint(0, 9)) for _ in range(10)]) for w in words}
    
    # System 4: Complexity scaling
    loops = max(1, depth // 4)
    for _ in range(loops):
        # System 2: 12-digit sequencing
        _logic = [f"{str(i).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(10)])}" for i in range(len(words))]
    return True

def synthesize_response(prompt, context_df):
    """
    SYSTEM 3: THE SYNTHESIS WIRE
    This mimics an AI by building an answer from your data blocks.
    """
    # 1. Intent Scan
    topics = context_df['Topic'].fillna('').tolist()
    match, score = process.extractOne(prompt, topics, scorer=fuzz.token_set_ratio)
    
    # 2. Construction Matrix
    if score >= 75:
        data_block = context_df[context_df['Topic'] == match].iloc[-1]['Meaning']
        
        # We "Synthesize" the answer to make it direct
        if "top" in prompt.lower() or "best" in prompt.lower():
            prefixes = ["According to current data nodes, ", "Synthesis reveals that ", "The primary entry is "]
            return f"{random.choice(prefixes)}{data_block} is the leading choice in this sector."
        else:
            return data_block
    else:
        # Fallback if the bot doesn't know the specific topic yet
        return "System 3: Inquiry analyzed. Current Context Sheet does not contain a stable data-block for this query. Please update the Admin Panel."

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Synthetic Core")
    st.caption("OFFLINE GENERATIVE ENGINE | SYSTEMS 1-4 ACTIVE")

    if "onion_msgs" not in st.session_state: 
        st.session_state.onion_msgs = []

    # Display Chat History
    for msg in st.session_state.onion_msgs:
        with st.chat_message(msg["role"]): 
            st.markdown(msg["content"])

    if prompt := st.chat_input("Communicate with the Onion..."):
        # 1. Record User Intent
        st.session_state.onion_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): 
            st.markdown(prompt)

        # 2. Run Background Systems
        run_onion_math(prompt, len(st.session_state.onion_msgs))

        # 3. System 3 & 4: Synthesis
        with st.status("🧅 Peeling layers and synthesizing from Context Sheet...", expanded=False) as status:
            try:
                # Get your actual data from GSheets
                context_df = cortex.conn.read(worksheet="Context", ttl="1s")
                
                # Use the local "AI" engine to build the answer
                final_answer = synthesize_response(prompt, context_df)
                
                status.update(label="Synthesis Complete", state="complete")
            except:
                final_answer = "🚨 CRITICAL ERROR: Could not read Context Sheet. Verify your GSheet connection."
                status.update(label="Synthesis Failed", state="error")

        # 4. Final Output
        with st.chat_message("assistant"): 
            st.markdown(final_answer)
            
        st.session_state.onion_msgs.append({"role": "assistant", "content": final_answer})
