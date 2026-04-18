import streamlit as st
import cortex # Import the brain

def run():
    cortex.apply_theme("cyberpunk")
    st.title("🧠 BDL Think")
    
    with st.sidebar:
        st.markdown("### 🏒 Performance Panel")
        sport = st.toggle("🏃 Sport Mode", value=False)
        st.caption("Sport mode provides high-speed summaries.")

    prompt = st.chat_input("Enter Topic for Global Web Scan...")
    if prompt:
        with st.chat_message("user"): 
            st.markdown(prompt)
            
        with st.status("📡 Rerouting through Global Grid...", expanded=True):
            # USE THE CORTEX ENGINE WE JUST UPDATED
            res = cortex.run_deepthink_engine(prompt, sport=sport)
        
        with st.chat_message("assistant"):
            st.markdown(res)
