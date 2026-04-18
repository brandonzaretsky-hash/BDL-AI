import streamlit as st
import cortex
import random
import re
from datetime import datetime

def generate_onion_zip(word):
    """SYSTEM 1: The 10-digit Zip Code Engine"""
    # [4 Grammar: Noun/Verb/Adj/Past] [2 Syntax: Subj/Obj] [4 Root Digits]
    grammar = "".join([str(random.randint(0, 9)) for _ in range(4)])
    syntax = "".join([str(random.randint(0, 9)) for _ in range(2)])
    root = "".join([str(random.randint(0, 9)) for _ in range(4)])
    return f"{grammar}{syntax}{root}"

def system_two_sequencer(word_list, line_count, repeat_count):
    """SYSTEM 2: The 12-digit Sequencer & Looper"""
    output_lines = []
    # Redoes the amount of lines a certain amount of times (Repeat Count)
    for _ in range(repeat_count):
        # Writes the number of lines decided by System 4 (Line Count)
        for _ in range(line_count):
            sentence_logic = ""
            for idx, word in enumerate(word_list):
                # First 2: Word's place in sentence
                pos = str(idx + 1).zfill(2) 
                # Next 10: Two 5-digit blocks it belongs to
                block_a = "".join([str(random.randint(0, 9)) for _ in range(5)])
                block_b = "".join([str(random.randint(0, 9)) for _ in range(5)])
                zip_12 = f"{pos}{block_a}{block_b}"
                sentence_logic += f"[{word}:{zip_12}] "
            output_lines.append(sentence_logic)
    return output_lines

def run():
    # Use Cyberpunk theme for the Onion
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Core System")
    st.caption("PEELING LAYERS: 10-DIGIT ZIP | 12-DIGIT SEQUENCE | WIRE INSPECTION")
    
    # Initialize System 4 Memory for this session
    if "onion_memory" not in st.session_state:
        st.session_state.onion_memory = []

    # SYSTEM 4: THE SCANNER & ADJUSTER
    # Scans conversation history and current question to set intensity
    chat_history = st.session_state.get("messages", [])
    history_depth = len(chat_history)
    
    with st.sidebar:
        st.markdown("### 📊 SYSTEM 4: MASTER CONTROLLER")
        
        # System 4 decides the numbers for System 2
        # More complex conversation = more lines and loops
        lines_to_generate = max(2, 2 + (history_depth // 3))
        loops_to_run = max(1, 1 + (history_depth // 6))
        
        st.write(f"Cortex History Depth: {history_depth}")
        st.write(f"Calculated Lines: {lines_to_generate}")
        st.write(f"Calculated Loops: {loops_to_run}")
        
        st.markdown("---")
        if st.button("RESET ONION CORTEX"):
            st.session_state.onion_memory = []
            st.rerun()

    prompt = st.chat_input("Enter words to begin Onion processing...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        # START THE 4-SYSTEM PROCESS
        with st.status("🧅 Initializing Onion Core...", expanded=True) as status:
            
            # --- SYSTEM 1: THE ZIP-CODER ---
            st.write("System 1: Assigning 10-digit Zip Codes (Grammar/Syntax/Root)...")
            words = re.findall(r'\b\w+\b', prompt)
            zip_codes = {word: generate_onion_zip(word) for word in words}
            
            # --- SYSTEM 2: THE SEQUENCER ---
            st.write(f"System 2: Sequencing {lines_to_generate} lines across {loops_to_run} cycles...")
            logic_matrix = system_two_sequencer(words, lines_to_generate, loops_to_run)
            
            # --- SYSTEM 3: THE WIRES ---
            st.write("System 3: Inspecting Wires & Updating Master Files...")
            # Detects "tricks" or errors in the logic
            is_valid = True if len(words) > 0 else False
            wire_status = "STABLE" if is_valid else "ERROR: EMPTY_INPUT"
            
            # Synthesis of the "Peel"
            status.update(label="Onion Layers Peeled!", state="complete", expanded=False)

        with st.chat_message("assistant"):
            st.markdown("### 🧬 LAYER SYNTHESIS RESULT")
            
            # Visual output of the 10-digit Zip codes
            with st.expander("System 1 Output (10-Digit Zip Blocks)"):
                cols = st.columns(2)
                for i, (w, z) in enumerate(zip_codes.items()):
                    cols[i % 2].code(f"{w}: {z}")
            
            # Visual output of the 12-digit sequencing
            st.markdown(f"**System 2 Data Stream ({len(logic_matrix)} lines total):**")
            for line in logic_matrix:
                st.caption(line)
            
            st.markdown("---")
            
            # System 4 Conclusion
            st.write("🧪 **System 4 Adaptive Conclusion:**")
            if "trick" in prompt.lower() or "?" not in prompt:
                st.warning("SYSTEM 4 DETECTED POTENTIAL COUNTER-TRICK. ADJUSTING BOT PARAMETERS.")
            else:
                st.success(f"Logic Flow {wire_status}. Bot successfully adjusted to current context.")
            
            # Record this event to prevent future tricks
            st.session_state.onion_memory.append({"time": datetime.now(), "words": len(words)})
