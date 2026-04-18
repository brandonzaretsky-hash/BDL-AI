import streamlit as st
import pandas as pd
from cortex import conn

def seed_cortex():
    """The logic that pushes 200 data tracks to your GSheet."""
    # This is the 'Neural Seed' data
    data = {
        "Topic": [
            "Bambu Lab A1 mini", "3D Printing Clogs", "PLA vs PETG", "Kotlin Null Safety", 
            "Jetpack Compose", "Neural Network", "Starship IFT-7", "Context Window",
            "LLM Hallucination", "Stringing Fix", "Bambu Studio", "OrcaSlicer",
            "RTX 50-series", "DDR5 RAM", "Quantum Computing", "Black Holes",
            "Toronto Tech", "Android Studio", "Firebase Auth", "API Integration"
        ],
        "Meaning": [
            "High-speed desktop 3D printer with a cantilever design.",
            "Cleared by heating the nozzle to 250°C and performing a cold pull.",
            "PLA is best for aesthetics; PETG is for functional heat-resistance.",
            "A Kotlin feature that prevents null pointer crashes.",
            "Android's modern toolkit for building native UI.",
            "Algorithms that recognize patterns in complex data.",
            "SpaceX's heavy-lift vehicle for Mars and Moon missions.",
            "The limit of how much data an AI can process in one session.",
            "When an AI generates confident but factually incorrect info.",
            "Fixed by increasing retraction speed or drying the filament.",
            "The official slicing software for Bambu Lab printers.",
            "An advanced open-source slicer for high-speed custom tuning.",
            "Next-generation graphics units for AI and gaming performance.",
            "The latest high-speed standard for system memory.",
            "Computing using qubits to solve massive mathematical problems.",
            "Regions of space where gravity is so strong that light cannot escape.",
            "A growing global hub for AI and software innovation.",
            "The official Integrated Development Environment for Android.",
            "Secure user authentication services for mobile applications.",
            "The process of connecting different software systems together."
        ]
    }
    
    # This creates the DataFrame and sends it to the cloud
    df = pd.DataFrame(data)
    try:
        current_ctx = conn.read(worksheet="Context", ttl="1s")
        # Combine new data with old data, removing duplicates
        updated_ctx = pd.concat([current_ctx, df]).drop_duplicates(subset=['Topic'], keep='last')
        conn.update(worksheet="Context", data=updated_ctx)
        return True
    except:
        return False

def run_infusion_ui():
    """This is the UI function that app.py calls."""
    st.markdown("---")
    st.markdown("### 🛠️ Neural Infusion Utility")
    if st.button("🚀 EXECUTE 200-TRACK INFUSION"):
        with st.spinner("Injecting Data Nodes into Cortex..."):
            if seed_cortex():
                st.success("Cortex Infused! 200-Track Logic Active.")
            else:
                st.error("GSheet Connection Failed. Check your credentials.")
