import streamlit as st
import cortex
import random
import re
import wikipedia
import wikipediaapi
from fuzzywuzzy import fuzz, process

def run_background_onion_logic(prompt, history_depth):
    """
    Runs Systems 1, 2, and 4 in the background.
    No output is shown to the user, but the math is executed.
    """
    # SYSTEM 1: Zip Generation
    words = re.findall(r'\b\w+\b', prompt)
    zips = {w: "".join([str(random.randint(0, 9)) for _ in range(10)]) for w in words}
    
    # SYSTEM 4: Complexity Decision
    lines_to_gen = max(1, 1 + (history_depth // 4))
    loops_to_run = max(1, 1 + (history_depth // 8))
    
    # SYSTEM 2: 12-digit Sequence Execution
    for _ in range(loops_to_run):
        for _ in range(lines_to_gen):
            # The math happens here, but we don't return it to the UI
            _temp_logic = [f"{str(i).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(10)])}" for i in range(len(words))]
            
    return True

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧅 BDL Onion: Global Synthesis")
    st.caption("DEEP WEB SCAN | SYSTEM 1-4 ACTIVE (HIDDEN)")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display clean chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Enter your inquiry for the Onion..."):
        # 1. Record User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Process Background Onion Logic (Systems 1, 2, & 4)
        run_background_onion_logic(prompt, len(st.session_state.messages))

        # 3. SYSTEM 3: THE WIRES (Web Research & Grammar Synthesis)
        with st.status("📡 Scanning Web Grid & Peeling Layers...", expanded=True) as status:
            st.write("System 1-2: Indexing zip-blocks...")
            
            # Multi-source Scan (Simulating 10 pages via multiple Wikipedia hits)
            st.write("System 3: Searching first 10 data nodes...")
            wiki_wiki = wikipediaapi.Wikipedia(user_agent='BDL-AI/1.0', language='en')
            search_results = wikipedia.search(prompt, results=5) # Scan top 5-10 related nodes
            
            aggregated_context = ""
            for result in search_results:
                page = wiki_wiki.page(result)
                if page.exists():
                    # We take snippets from multiple "pages" to build the summary
                    aggregated_context += page.summary[:500] + " "
            
            if not aggregated_context:
                # Fallback to local Context sheet if web is blank
                try:
                    ctx_df = cortex.conn.read(worksheet="Context", ttl="1s")
                    topics = ctx_df['Topic'].fillna('').tolist()
                    match, score = process.extractOne(prompt, topics, scorer=fuzz.token_set_ratio)
                    if score >= 80:
                        aggregated_context = ctx_df[ctx_df['Topic'] == match].iloc[-1]['Meaning']
                except: pass

            st.write("System 4: Formatting grammar and syntax...")
            
            # Construct the final "Proper" answer
            if aggregated_context:
                # Basic cleanup to ensure "Proper Grammar and Stuff"
                final_answer = aggregated_context.strip()
                if not final_answer.endswith('.'): final_answer += "."
                # Capitalize first letter if needed
                final_answer = final_answer[0].upper() + final_answer[1:]
            else:
                final_answer = "The Onion has scanned the requested depth but could not synthesize a stable result from the current internet nodes."

            status.update(label="Synthesis Complete", state="complete")

        # 4. Assistant Output (Clean, no technical clutter)
        with st.chat_message("assistant"):
            st.markdown(final_answer)
        
        # Save to history
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
