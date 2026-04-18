import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Database Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def apply_theme(style_type):
    if style_type == "cyberpunk":
        st.markdown("""
            <style>
            .stApp { background-color: #000; background-image: radial-gradient(circle at 50% 50%, rgba(255, 0, 255, 0.1) 0%, rgba(0, 0, 0, 1) 70%); }
            p, span, div, li, label { color: #00ff41 !important; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #00ff41; }
            section[data-testid="stSidebar"] { background-color: #051a05; border-right: 2px solid #FF8C00; }
            .stButton>button { background-color: #000; color: #00FFFF; border: 1px solid #00FFFF; width: 100%; }
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
        c = conn.read(worksheet="Context", ttl="1s")
        # Only count nodes that you have approved
        return len(c[c['Status'] == 'Approved'])
    except: return 0
