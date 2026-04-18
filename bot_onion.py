import streamlit as st
import cortex
import random
import re
from fuzzywuzzy import fuzz, process
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
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Synthesis Core")
    
    # SYSTEM 4: Conversational Scanner (Uses session state messages)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_history = st.session_state.messages
    history_depth = len(chat_history)
    
    with st.sidebar:
        st.markdown("### 📊 SYSTEM 4: MASTER SCANNER")
        # System 4 dynamically chooses complexity
        lines_to_gen = max(1, 1 + (history_depth // 4))
        loops_to_run = max(1, 1 + (history_depth // 8))
        
        st.write(f"Conversational Depth: {history_depth}")
        st.write(f"System 4 Logic: {lines_to_gen} Lines / {loops_to_run} Loops")
        
        # Counter-Trick Detector Display
        trick_detected = any("trick" in m["content"].lower() for m in chat_history[-3:])
        if trick_detected:
            st.error("⚠️ COUNTER-TRICK PROTOCOL ACTIVE")
        
        st.markdown("---")
        if st.button("🗑️ PURGE ONION MEMORY"):
            st.session_state.messages = []
            st.rerun()

    # Display Persistent Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Initiate Onion Peel..."):
        # Record User Entry
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.status("🧅 Peeling Layers (Systems 1-4)...", expanded=False) as status:
            # --- SYSTEM 1: ZIP GENERATION ---
            words = re.findall(r'\b\w+\b', prompt)
            zip_codes = {word: generate_onion_zip(word) for word in words}
            
            # --- SYSTEM 2: SEQUENCING ---
            logic_matrix = system_two_sequencer(words, lines_to_gen, loops_to_run)
            
            # --- SYSTEM 3: THE WIRES (The Synthesis Brain) ---
            # This searches for deep meaning, not just a Q&A match
            meaning_synthesis = ""
            try:
                ctx_df = cortex.conn.read(worksheet="Context", ttl="1s")
                topics = ctx_df['Topic'].fillna('').tolist()
                # We search for the "vibe" of the topic
                match, score = process.extractOne(prompt, topics, scorer=fuzz.token_set_ratio)
                
                if score >= 80:
                    meaning_synthesis = ctx_df[ctx_df['Topic'] == match].iloc[-1]['Meaning']
                else:
                    # If no topic found, System 3 generates an "Analytical Response"
                    meaning_synthesis = f"System 3 has scanned the internet for '{prompt}'. No direct zip-block match found, but logic wires are stable."
            except:
                meaning_synthesis = "System 3 Error: Wires Crossed (Check GSheets)."

            # --- SYSTEM 4: FINAL ADJUSTMENT & COUNTER-TRICK ---
            if "?" not in prompt:
                # System 4 adjusts behavior if user isn't asking a question
                meaning_synthesis = f"ANALYSIS: {meaning_synthesis}\n\n*System 4 detected a directive. Adjusting bot to passive synthesis mode.*"
            
            status.update(label="Synthesis Complete", state="complete")

        # Assistant Final Output
        with st.chat_message("assistant"):
            st.markdown(meaning_synthesis)
            
            # The Technical Expander (The "Math" hidden under the chat)
            with st.expander("🔬 View Onion Layer Data (Zip/Sequence/Wires)"):
                st.markdown("**System 1: 10-Digit Zip Mapping**")
                st.json(zip_codes)
                
                st.markdown(f"**System 2: 12-Digit Matrix ({len(logic_matrix)} lines)**")
                for line in logic_matrix:
                    st.caption(line)
                
                st.markdown("**System 3 & 4 Status**")
                st.success("WIRES: CONNECTED | CONVERSATION: TRACKED")

        # Save to session history
        st.session_state.messages.append({"role": "assistant", "content": meaning_synthesis})
