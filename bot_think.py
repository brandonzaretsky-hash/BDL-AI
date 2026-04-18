import streamlit as st
import cortex, wikipedia
from fuzzywuzzy import fuzz, process

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧠 BDL Think: Auto-Scout")
    
    if prompt := st.chat_input("Enter a word or topic to scout..."):
        with st.status("🔍 Scanning Cortex...", expanded=True) as status:
            all_df = cortex.conn.read(worksheet="Context", ttl="1s")
            # Only search things we already approved
            approved_df = all_df[all_df['Status'] == 'Approved']
            topics = approved_df['Topic'].fillna('').tolist()
            
            match, score = process.extractOne(prompt, topics, scorer=fuzz.token_set_ratio)
            
            if score >= 85:
                ans = approved_df[approved_df['Topic'] == match].iloc[-1]['Meaning']
                st.write("✅ Knowledge already active in Onion.")
            else:
                st.write(f"🛰️ '{prompt}' unknown. Accessing global satellite data...")
                try:
                    wikipedia.set_lang("en")
                    summary = wikipedia.summary(prompt, sentences=2)
                    # AUTO-ADD TO DICTIONARY (as Pending)
                    cortex.update_onion_context(prompt.title(), summary, status="Pending")
                    ans = f"DATA SCOUTED: {summary}\n\n⚠️ *This is PENDING. Approve it in the sidebar to teach the Onion.*"
                except:
                    ans = "System Error: No global data found. Try a different keyword."
            
            status.update(label="Scout Complete", state="complete")
            st.info(ans)
