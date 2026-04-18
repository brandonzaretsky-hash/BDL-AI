import streamlit as st
import cortex, wikipedia, wikipediaapi

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧬 BDL DNA")
    target = st.text_input("Enter Name for Genealogy Scan")
    if st.button("Scan") and target:
        with st.status("Scanning DNA records..."):
            wiki = wikipediaapi.Wikipedia(user_agent='BDL-AI/1.0', language='en')
            page = wiki.page(target)
            if page.exists():
                st.markdown(f"### 🌳 TREE: {page.title}")
                st.write(page.summary[:1000])
                connections = [c for c in ["married", "spouse", "born to", "children", "son"] if c in page.text.lower()]
                st.info(f"Detected Connections: {', '.join(connections) if connections else 'None'}")
            else: st.error("Target not found.")
