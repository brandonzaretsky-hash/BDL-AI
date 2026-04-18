import streamlit as st
import cortex
import random
import re
import wikipedia
import wikipediaapi
from fuzzywuzzy import fuzz, process

def run_background_onion_logic(prompt, history_depth):
    """
    SYSTEMS 1, 2, & 4: INTERNAL MAPPING
    Executes the 10-digit and 12-digit numbering systems in the background.
    """
    words = re.findall(r'\b\w+\b', prompt)
    # System 1: Zip Mapping
    zips = {w: "".join([str(random.randint(0, 9)) for _ in range(10)]) for w in words}
    
    # System 4: Complexity Calibration
    lines_to_gen = max(1, 1 + (history_depth // 4))
    loops_to_run = max(1, 1 + (history_depth // 8))
    
    # System 2: Sequence Looping
    for _ in range(loops_to_run):
        for _ in range(lines_to_gen):
            _temp = [f"{str(i).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(10)])}" for i in range(len(words))]
    return True

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Intent Synthesis")
    st.caption("CORE SYSTEMS 1-4 ACTIVE | DIRECT DATA RETRIEVAL")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display clean chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Input your query..."):
        # 1. Record User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Execute Hidden Logic
        run_background_onion_logic(prompt, len(st.session_state.messages))

        # 3. SYSTEM 3: DIRECT SYNTHESIS (Intent Filtering)
        with st.status("📡 Peeling to Core Intent...", expanded=True) as status:
            st.write("System 1: Calculating word zips...")
            st.write("System 3: Scanning 10 data nodes for direct answers...")
            
            wiki_wiki = wikipediaapi.Wikipedia(user_agent='BDL-AI/1.0', language='en')
            search_results = wikipedia.search(prompt, results=8)
            
            full_data = ""
            for result in search_results:
                page = wiki_wiki.page(result)
                if page.exists():
                    full_data += page.text[:2000] + " " # Pulling deeper text to find the answer

            st.write("System 4: Neutralizing 'Fluff' and defining answer blocks...")

            # --- INTENT FILTERING LOGIC ---
            # We look for specific answer patterns and remove "Definition" sentences
            # This simulates the bot actually knowing what you're asking for.
            
            lines = full_data.split('.')
            answer_segments = []
            
            # Filter out "X is a..." or "X is defined as..." or "X was invented by..."
            filter_keywords = ["is a", "is the process", "is defined", "refer to", "commonly known as"]
            
            for line in lines:
                # If the line contains brands, rankings, or specific answers, keep it.
                if any(kw in line.lower() for kw in ["top", "best", "leading", "popular", "brand", "model", "vs"]):
                    # Avoid the basic definitions
                    if not any(fk in line.lower() for fk in filter_keywords[:3]):
                        answer_segments.append(line.strip())
            
            if len(answer_segments) > 2:
                # Construct answer from specific segments
                final_answer = ". ".join(answer_segments[:3]) + "."
            elif full_data:
                # If specific answer segments are sparse, summarize the core data but skip the first paragraph
                sections = full_data.split('\n\n')
                final_answer = sections[1][:1000] if len(sections) > 1 else full_data[:1000]
            else:
                final_answer = "The Onion could not locate a stable data node for this specific query."

            # Final Polish
            final_answer = re.sub(r'\[.*?\]', '', final_answer) # Remove wiki brackets
            
            status.update(label="Synthesis Complete", state="complete")

        # 4. Final Output
        with st.chat_message("assistant"):
            st.markdown(final_answer)
        
        # Save to history
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
