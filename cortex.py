
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Database Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def apply_theme(style_type):
    if style_type == "cyberpunk":
        st.markdown("""
            <style>
            /* The Main App Background */
            .stApp { 
                background-color: 1000, 100, 118; 
                background-image: radial-gradient(circle at 50% 50%, rgba(255, 0, 255, 0.1) 0%, rgba(255, 0, 255, 0.1) 70%); 
            }
            
            /* High-Tech Font & Glow */
            h1 { color: #FF00FF !important; text-shadow: 0 0 15px #FF00FF; text-align: center; font-weight: bold; }
            h2, h3 { color: #00FFFF !important; text-shadow: 0 0 10px #00FFFF; }
            p, span, div, li, label { color: #66f7ff !important; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #66f7ff; }
            
            /* Sidebar Styling */
            section[data-testid="stSidebar"] { background-color: #051a05; border-right: 2px solid #FF8C00; }
            
            /* Neon Buttons */
            .stButton>button { 
                background-color: #000; 
                color: #00FFFF; 
                border: 1px solid #00FFFF; 
                box-shadow: 0 0 10px #00FFFF; 
                transition: 0.3s;
            }
            .stButton>button:hover { 
                border: 1px solid #FF8C00; 
                color: #FF8C00; 
                box-shadow: 0 0 20px #FF8C00; 
            }

            /* The Missing UI Cards */
            .bot-card { 
                height: 220px; 
                display: flex; 
                flex-direction: column; 
                justify-content: center; 
                align-items: center; 
                text-align: center; 
                border: 2px solid #333; 
                border-radius: 15px; 
                background: rgba(0,0,0,0.5);
                margin-bottom: 15px;
            }
            .bot-card:hover { border: 1px solid #66f7ff; box-shadow: 0 0 15px #66f7ff; }

            /* Large Score Counter */
            .intel-counter { 
                font-size: 50px; 
                text-align: center; 
                border: 2px solid #66f7ff; 
                padding: 15px; 
                border-radius: 15px; 
                box-shadow: 0 0 20px rgba(0, 255, 65, 0.2); 
                margin-bottom: 30px; 
            }
            </style>
            """, unsafe_allow_html=True)

def update_onion_context(topic, meaning, status="Pending"):
    try:
        df = conn.read(worksheet="Context", ttl="1s")
        new_row = pd.DataFrame([{"Topic": topic, "Meaning": meaning, "Status": status}])
        updated_df = pd.concat([df, new_row], ignore_index=True).drop_duplicates(subset=['Topic'], keep='last')
        conn.update(worksheet="Context", data=updated_df)
        return True
    except: return False

def get_total_intelligence():
    try:
        c = conn.read(worksheet="Context", ttl="1s")
        return len(c[c['Status'] == 'Approved'])
    except: return 0
