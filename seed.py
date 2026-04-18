import streamlit as st
import pandas as pd
from cortex import conn

def seed_cortex():
    data = {
        "Topic": ["Bambu Lab A1 mini", "Kotlin Null Safety", "Starship IFT-7", "Neural Network"],
        "Meaning": ["3D Printer", "Code Safety", "SpaceX Rocket", "AI Brain"]
    }
    df = pd.DataFrame(data)
    
    try:
        # TEST 1: Can we even see the sheet?
        st.write("🔍 Testing Connection...")
        current_ctx = conn.read(worksheet="Context", ttl="1s")
        st.write(f"✅ Connection Stable. Found {len(current_ctx)} existing rows.")
        
        # TEST 2: Attempting the Write
        st.write("📡 Attempting Infusion...")
        updated_ctx = pd.concat([current_ctx, df]).drop_duplicates(subset=['Topic'], keep='last')
        conn.update(worksheet="Context", data=updated_ctx)
        return True, "Success"
    except Exception as e:
        # THIS WILL TELL US THE REAL PROBLEM
        return False, str(e)

def run_infusion_ui():
    st.markdown("### 🧪 Diagnostic Infusion")
    if st.button("🚀 RUN DIAGNOSTIC"):
        success, error_msg = seed_cortex()
        if success:
            st.success("Cortex Infused! Check your sheet now.")
        else:
            st.error(f"🚨 INFUSION BLOCKED: {error_msg}")
            if "not found" in error_msg.lower():
                st.info("💡 Hint: Your GSheet might be missing a tab named 'Context'.")
            elif "permission" in error_msg.lower():
                st.info("💡 Hint: Set your GSheet to 'Anyone with the link can Edit'.")
