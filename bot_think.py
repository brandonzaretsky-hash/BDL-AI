import streamlit as st
import cortex, wikipedia
from fuzzywuzzy import fuzz, process

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧠 BDL Think: Scout Mode")
    
    if prompt := st.chat_input("Search for new knowledge..."):
        with st.status("🔍 Scanning Cortex...", expanded=True) as status:
            ctx_df = cortex.conn.read(worksheet="Context", ttl="1s")
            # Filter for approved topics
            approved_df = ctx_df[ctx_df['Status'] == 'Approved']
            topics = approved_df['Topic'].fillna('').tolist()
            
            match, score = process.extractOne(prompt, topics, scorer=fuzz.token_set_ratio)
            
            if score >= 85:
                ans = approved_df[approved_df['Topic'] == match].iloc[-1]['Meaning']
                st.write("✅ Knowledge already exists in Approved Cortex.")
            else:
                st.write("🛰️ Unknown topic. Fetching from Global Nodes...")
                try:
                    wikipedia.set_lang("en")
                    summary = wikipedia.summary(prompt, sentences=2)
                    # Save as PENDING
                    cortex.update_onion_context(prompt.title(), summary, status="Pending")
                    ans = f"NEW DATA SCOUTED: {summary}\n\n⚠️ *This node is PENDING approval from an Admin.*"
                except:
                    ans = "System Error: No global data found for this node."
            
            status.update(label="Scan Complete", state="complete")
            st.info(ans)
