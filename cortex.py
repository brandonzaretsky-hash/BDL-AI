import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS # MUST HAVE THIS
import io # MUST HAVE THIS
import re, wikipedia, wikipediaapi, requests
from datetime import datetime

# Shared Connection
conn = st.connection("gsheets", type=GSheetsConnection)

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
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<style>.online-indicator { color: #4CAF50; font-weight: bold; }</style>", unsafe_allow_html=True)

def get_total_intelligence():
    try:
        m = conn.read(worksheet="Memory", ttl="1s")
        c = conn.read(worksheet="Context", ttl="1s")
        return len(m) + len(c)
    except: return 0

# --- THE CRASH FIX: ADDED EXTRA SAFETY ---
def show_voices(e, t, code, choice):
    try:
        v1, v2 = st.columns(2)
        with v1:
            try:
                tts_e = gTTS(e[:1000], lang='en')
                f_e = io.BytesIO()
                tts_e.write_to_fp(f_e)
                st.audio(f_e)
            except: st.caption("English Audio Grid Offline")
            
        # Only try translation voice if it's not "None" and code is valid
        if t and choice != "None" and code != "none":
            with v2:
                try:
                    tts_t = gTTS(t[:1000], lang=code)
                    f_t = io.BytesIO()
                    tts_t.write_to_fp(f_t)
                    st.audio(f_t)
                except: st.caption("Translation Audio Grid Offline")
    except:
        pass # If columns fail, just don't show audio
