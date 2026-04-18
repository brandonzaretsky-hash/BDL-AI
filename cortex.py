*import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

def apply_theme(style_type):
    if style_type == "cyberpunk":
        st.markdown("""
            <style>
            .stApp { background-color: #000; }
            p, span, div, label { color: #00ff41 !important; font-family: 'Courier New', monospace; }
            .stButton>button { width: 100%; border: 1px solid #00ff41; background: black; color: #00ff41; }
            </style>
            """, unsafe_allow_html=True)

def update_onion_context(topic, meaning, status="Pending"):
    try:
        df = conn.read(worksheet="Context", ttl="1s")
        new_row = pd.DataFrame([{"Topic": topic, "Meaning": meaning, "Status": status}])
        updated_df = pd.concat([df, new_row], ignore_index=True).drop_duplicates(subset=['Topic'], keep='last')
        conn.update(worksheet="Context", data=updated_df)
        return True
    except:
        return False

def get_total_intelligence():
    try:
        # Only count approved nodes
        c = conn.read(worksheet="Context", ttl="1s")
        return len(c[c['Status'] == 'Approved'])
    except: return 0
