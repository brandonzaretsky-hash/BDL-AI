import streamlit as st
import cortex, wikipedia
from fuzzywuzzy import fuzz, process

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧠 BDL Think: Scout")
    
    if prompt := st.chat_input("Enter a new node to scout..."):
        with st.status("🧅 Peeling Layers & Scanning Global Nodes...", expanded=True) as status:
            all_df = cortex.conn.read(worksheet="Context", ttl="1s")
            approved_df = all_df[all_df['Status'] == 'Approved']
            topics = approved_df['Topic'].fillna('').tolist()
            
            match, score = process.extractOne(prompt, topics, scorer=fuzz.token_set_ratio)
            
            if score >= 85:
                ans = approved_df[approved_df['Topic'] == match].iloc[-1]['Meaning']
                status.update(label="Node already active in Cortex.", state="complete")
            else:
                try:
                    wikipedia.set_lang("en")
                    summary = wikipedia.summary(prompt, sentences=2)
                    cortex.update_onion_context(prompt.title(), summary, status="Pending")
                    ans = f"NEW DATA SCOUTED: {summary}\n\n⚠️ *Pending approval in Sidebar.*"
                    status.update(label="New Data Captured!", state="complete")
                except:
                    ans = "System Error: No global data found."
                    status.update(label="Scout Failed.", state="error")
            
            st.info(ans)
