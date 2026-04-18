import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS
import io, re, wikipedia, wikipediaapi, requests
from datetime import datetime

# 1. Setup the Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. THE THEME ENGINE (Make sure this is named exactly like this)
def apply_theme(style_type):
    if style_type == "cyberpunk":
        st.markdown("""
            <style>
            .stApp { background-color: #000; background-image: radial-gradient(circle at 50% 50%, rgba(255, 0, 255, 0.12) 0%, rgba(0, 0, 0, 1) 70%), linear-gradient(180deg, #000 0%, #051a05 100%); }
            h1 { color: #FF00FF !important; text-shadow: 0 0 15px #FF00FF; text-align: center; font-weight: bold; }
            h2, h3 { color: #00FFFF !important; text-shadow: 0 0 10px #00FFFF; text-align: center; }
            p, span, div, li { color: #00ff41 !important; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #00ff41; }
            section[data-testid="stSidebar"] { background-color: #051a05; border-right: 2px solid #FF8C00; }
            .stButton>button { background-color: #000; color: #00FFFF; border: 1px solid #00FFFF; box-shadow: 0 0 15px #00FFFF; width: 100%; height: 50px; }
            .stButton>button:hover { border: 1px solid #FF8C00; color: #FF8C00; box-shadow: 0 0 20px #FF8C00; }
            .intel-counter { font-size: 50px; text-align: center; border: 2px solid #00ff41; padding: 20px; border-radius: 15px; box-shadow: inset 0 0 30px rgba(0, 255, 65, 0.3), 0 0 20px rgba(0, 255, 65, 0.2); margin-bottom: 30px; background: rgba(0, 255, 65, 0.03); }
            .bot-card { height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; margin-bottom: 10px; }
            .dev-box { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; }
            .caution-tape { position: absolute; top: 40px; left: -25px; width: 200px; height: 30px; background-color: #FF8C00; color: #000; font-weight: 1000; transform: rotate(-25deg); text-align: center; line-height: 30px; box-shadow: 0 0 20px #FF8C00; font-family: 'Impact', sans-serif; font-size: 16px; z-index: 10; }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<style>.online-indicator { color: #4CAF50; }</style>", unsafe_allow_html=True)

# 3. Intelligence Counter
def get_total_intelligence():
    try:
        m = conn.read(worksheet="Memory", ttl="1s")
        c = conn.read(worksheet="Context", ttl="1s")
        return len(m) + len(c)
    except: return 0
