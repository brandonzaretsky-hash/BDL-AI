import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from gtts import gTTS
import io, re, wikipedia, wikipediaapi, requests
from datetime import datetime

# 1. Establish the Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Theme Engine
def apply_theme(style_type):
    if style_type == "cyberpunk":
        st.markdown("""
            <style>
            .stApp {
                background-color: #000000;
                background-image: radial-gradient(circle at 50% 50%, rgba(255, 0, 255, 0.1) 0%, rgba(0, 0, 0, 1) 70%);
            }
            h1 { color: #FF00FF !important; text-shadow: 0 0 15px #FF00FF; text-align: center; font-weight: bold; }
            h2, h3 { color: #00FFFF !important; text-shadow: 0 0 10px #00FFFF; }
            p, span, div, li, label { color: #00ff41 !important; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #00ff41; }

            section[data-testid="stSidebar"] {
                background-color: #051a05;
                border-right: 2px solid #FF8C00;
            }
            
            .stButton>button {
                background-color: #000; color: #00FFFF;
                border: 1px solid #00FFFF; box-shadow: 0 0 15px #00FFFF;
                width: 100%; height: 50px;
            }
            .stButton>button:hover {
                border: 1px solid #FF8C00; color: #FF8C00; box-shadow: 0 0 20px #FF8C00;
            }

            .intel-counter {
                font-size: 50px; text-align: center; color: #00FFFF !important;
                border: 2px solid #00ff41; padding: 20px; border-radius: 15px;
                box-shadow: inset 0 0 30px rgba(0, 255, 65, 0.3), 0 0 20px rgba(0, 255, 65, 0.2);
                margin-bottom: 30px;
            }
            
            .bot-card {
                height: 250px; display: flex; flex-direction: column; 
                justify-content: center; align-items: center;
                text-align: center; border: 1px solid #333; border-radius: 10px;
            }

            .dev-box { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; }
            .caution-tape {
                position: absolute; top: 40px; left: -25px;
                width: 200px; height: 30px;
                background-color: #FF8C00; color: #000; font-weight: 1000;
                transform: rotate(-25deg); text-align: center; line-height: 30px;
                box-shadow: 0 0 20px #FF8C00; font-family: 'Impact', sans-serif;
                font-size: 16px; z-index: 10;
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<style>p, span, div { color: #4CAF50; }</style>", unsafe_allow_html=True)

# 3. Intelligence Data Fetcher
def get_total_intelligence():
    try:
        m = conn.read(worksheet="Memory", ttl="1s")
        c = conn.read(worksheet="Context", ttl="1s")
        return len(m) + len(c)
    except: return 0

# 4. Voice Generator Engine
def show_voices(e, t, code, choice):
    try:
        v1, v2 = st.columns(2)
        with v1:
            try:
                tts_e = gTTS(e[:1000], lang='en')
                f_e = io.BytesIO()
                tts_e.write_to_fp(f_e)
                st.audio(f_e)
            except: pass
        if t and choice != "None" and code != "none":
            with v2:
                try:
                    tts_t = gTTS(t[:1000], lang=code)
                    f_t = io.BytesIO()
                    tts_t.write_to_fp(f_t)
                    st.audio(f_t)
                except: pass
    except: pass

# 5. Global Search Engine (for Think and DNA)
def run_deepthink_engine(q, sport=False):
    user_id = 'BDL-AI_Nexus/1.0 (Contact: bdl_nexus_dev@example.com)'
    try:
        search_results = wikipedia.search(q, results=3)
        if not search_results: return "❌ No records found."
        
        wiki_wiki = wikipediaapi.Wikipedia(user_agent=user_id, language='en')
        page = wiki_wiki.page(search_results[0])
        
        if not page.exists(): return "❌ Data Stream Offline."
        return page.summary[:1500] if sport else page.text[:5000]
    except:
        return "🚨 Grid Connection Error. Wikipedia blocked the request."
