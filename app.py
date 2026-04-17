import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS
from streamlit_lottie import st_lottie
import io, re, wikipedia, wikipediaapi, time, requests
from datetime import datetime

#--------------------
# Section 1: Setup & Session State
#--------------------
st.set_page_config(page_title="BDL.AI NEXUS", layout="wide", page_icon="🧠")

state_defaults = {
    "page": "Nexus Home",
    "messages": [],
    "has_run_splash": False,
    "onion_unlocked": False,
    "target_lang_code": "none",
    "deepthink_sport": False,
    "deepthink_strictness": 85,
    "waiting_for_answer": False,
    "last_question": ""
}
for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

#--------------------
# Section 2: Visual Themes (Cyberpunk Chroma)
#--------------------
def apply_theme(style_type):
    if style_type == "cyberpunk":
        st.markdown("""
            <style>
            .stApp {
                background-color: #000000;
                background-image: 
                    radial-gradient(circle at 50% 50%, rgba(255, 0, 255, 0.12) 0%, rgba(0, 0, 0, 1) 70%),
                    linear-gradient(180deg, #000 0%, #051a05 100%);
            }
            h1 { color: #FF00FF !important; text-shadow: 0 0 15px #FF00FF; text-align: center; font-weight: bold; }
            h2, h3, .online-indicator { color: #00FFFF !important; text-shadow: 0 0 10px #00FFFF; text-align: center; }
            p, span, div, li { color: #00ff41 !important; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #00ff41; }
            section[data-testid="stSidebar"] { background-color: #051a05; border-right: 2px solid #FF8C00; }
            .stButton>button { background-color: #000; color: #00FFFF; border: 1px solid #00FFFF; box-shadow: 0 0 15px #00FFFF; width: 100%; height: 50px; }
            .stButton>button:hover { border: 1px solid #FF8C00; color: #FF8C00; box-shadow: 0 0 20px #FF8C00; }
            .bot-card { height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; margin-bottom: 10px; }
            .dev-box { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; background: transparent; }
            .caution-tape { position: absolute; top: 40px; left: -35px; width: 220px; height: 35px; background-color: #FF8C00; color: #000; font-weight: 1000; transform: rotate(-25deg); text-align: center; line-height: 35px; box-shadow: 0 0 20px #FF8C00; font-family: 'Impact', sans-serif; font-size: 18px; z-index: 10; }
            .intel-counter { font-size: 50px; text-align: center; border: 2px solid #00ff41; padding: 20px; border-radius: 15px; box-shadow: inset 0 0 30px rgba(0, 255, 65, 0.3), 0 0 20px rgba(0, 255, 65, 0.2); margin-bottom: 30px; background: rgba(0, 255, 65, 0.03); }
            .admin-header { color: #FF8C00 !important; border-bottom: 2px solid #FF8C00; margin-top: 50px; padding-bottom: 10px; }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<style>.online-indicator { display: flex; align-items: center; justify-content: flex-end; color: #4CAF50; font-weight: bold; padding: 10px; }</style>", unsafe_allow_html=True)

#--------------------
# Section 3: Shared Core Engines
#--------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def get_total_intelligence():
    try:
        m = conn.read(worksheet="Memory", ttl="1s")
        c = conn.read(worksheet="Context", ttl="1s")
        return len(m) + len(c)
    except: return 0

def get_translation(text, target):
    try: return GoogleTranslator(source='auto', target=target).translate(text[:800])
    except: return None

def show_voices(e, t, code, choice):
    v1, v2 = st.columns(2)
    with v1:
        try:
            tts_e = gTTS(e[:3000], lang='en'); f_e = io.BytesIO(); tts_e.write_to_fp(f_e); st.audio(f_e)
        except: pass
    if t and choice != "None":
        with v2:
            try:
                tts_t = gTTS(t, lang=code); f_t = io.BytesIO(); tts_t.write_to_fp(f_t); st.audio(f_t)
            except: pass

def run_deepthink_engine(q, sport=False):
    wiki_wiki = wikipediaapi.Wikipedia(user_agent='BDL-AI/1.0', language='en')
    try:
        search_results = wikipedia.search(q, results=3)
        if not search_results: return "❌ No matching grid entries found."
        page = wiki_wiki.page(search_results[0])
        if not page.exists(): return "❌ Data stream offline."
        if sport: return f"🏃 **Sport Mode Summary:**\n\n{page.summary[:1500]}..."
        else: return f"📑 **Full Deepthink Analysis:**\n\n{page.text[:5000]}..."
    except Exception as e: return f"🚨 **Grid Error:** {str(e)}"

def save_context_request(topic, meaning, conn):
    df = conn.read(worksheet="ContextRequests", ttl="1s")
    new_req = pd.DataFrame([{"Topic": str(topic).strip(), "Meaning": str(meaning).strip(), "User": "External", "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")}])
    conn.update(worksheet="ContextRequests", data=pd.concat([df, new_req], ignore_index=True))

#--------------------
# PAGE: NEXUS HOME (Gateway V10.1)
#--------------------
def show_nexus_home():
    apply_theme("cyberpunk")
    with st.sidebar:
        st.title("🔑 Credentials")
        access_key = st.text_input("Enter Access Key", type="password")
        is_admin = (access_key == "admin") or (access_key == "qwerty")
        is_dev = (access_key == "qwerty")
    
    st.markdown("<h1>BDL.AI NEXUS GATEWAY</h1>", unsafe_allow_html=True)
    score = get_total_intelligence()
    st.markdown(f"<div class='intel-counter'><span>{score}</span><br><span style='font-size: 16px;'>SYNTHESIZED LESSONS IN CORTEX</span></div>", unsafe_allow_html=True)

    l_url = "https://lottie.host/8040d6c1-9031-4e76-9051-177b966b96e4/ZzQoUvV6wZ.json"
    try:
        r = requests.get(l_url, timeout=5)
        if r.status_code == 200: st_lottie(r.json(), height=200, speed=1.2)
    except: pass

    st.markdown("<h3>SELECT BOT MODULE TO ACTIVATE:</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='bot-card'><img src='https://img.icons8.com/neon/120/bot.png' width='100'/><h2>BDL</h2><p>The Original</p></div>", unsafe_allow_html=True)
        if st.button("INITIALIZE BDL"): st.session_state.page = "BDL Standard"; st.rerun()
    with c2:
        st.markdown("<div class='bot-card'><img src='https://img.icons8.com/neon/120/brain.png' width='100'/><h2>THINK</h2><p>Web Powerhouse</p></div>", unsafe_allow_html=True)
        if st.button("INITIALIZE THINK"): st.session_state.page = "BDL Deepthink"; st.rerun()
    with c3:
        st.markdown("<div class='bot-card'><div class='dev-box'><div class='caution-tape'>DEV-ONLY</div><div style='font-size: 80px;'>🧅</div></div><h2>ONION</h2><p>The All-in-One</p></div>", unsafe_allow_html=True)
        if st.button("INITIALIZE ONION"):
            if is_dev: st.session_state.page = "BDL Onion"; st.rerun()
            else: st.warning("Requires Dev Key.")
    with c4:
        st.markdown("<div class='bot-card'><div style='font-size: 80px;'>🧬</div><h2>DNA</h2><p>Family Tree Search</p></div>", unsafe_allow_html=True)
        if st.button("INITIALIZE DNA"): st.session_state.page = "BDL DNA New"; st.rerun()

    if is_admin:
        st.markdown("<h2 class='admin-header'>🛠️ NEXUS ADMIN COMMAND</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["📝 Q&A Requests", "📚 Cortex Training"])
        with t1:
            try:
                pending_qa = conn.read(worksheet="Requests", ttl="1s")
                if not pending_qa.empty:
                    st.dataframe(pending_qa, use_container_width=True)
                    qa_idx = st.number_input("Lesson ID", 0, len(pending_qa)-1, 0, key="qa_sel")
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✅ Approve Lesson"):
                            mem = conn.read(worksheet="Memory", ttl="1s"); row = pending_qa.iloc[[qa_idx]][['question', 'answer']]
                            conn.update(worksheet="Memory", data=pd.concat([mem, row], ignore_index=True))
                            conn.update(worksheet="Requests", data=pending_qa.drop(pending_qa.index[qa_idx])); st.rerun()
            except: pass
        with t2:
            try:
                pending_ctx = conn.read(worksheet="ContextRequests", ttl="1s")
                if not pending_ctx.empty:
                    st.dataframe(pending_ctx, use_container_width=True)
                    ctx_idx = st.number_input("Cortex ID", 0, len(pending_ctx)-1, 0, key="ctx_sel")
                    if st.button("✅ Approve Context"):
                        core = conn.read(worksheet="Context", ttl="1s"); row = pending_ctx.iloc[[ctx_idx]][['Topic', 'Meaning']]
                        conn.update(worksheet="Context", data=pd.concat([core, row], ignore_index=True))
                        conn.update(worksheet="ContextRequests", data=pending_ctx.drop(pending_ctx.index[ctx_idx])); st.rerun()
            except: pass

#--------------------
# PAGE: BDL STANDARD
#--------------------
def show_bdl_standard():
    apply_theme("standard")
    if st.sidebar.button("⬅️ EXIT"): st.session_state.page = "Nexus Home"; st.rerun()
    st.title("🤖 BDL Standard")
    with st.sidebar:
        lang_map = {"None": "none", "Hebrew": "iw", "French": "fr", "Spanish": "es", "German": "de", "Arabic": "ar", "Chinese": "zh-CN", "Japanese": "ja"}
        choice = st.selectbox("Select Language", list(lang_map.keys()))
        st.session_state.target_lang_code = lang_map[choice]
        voice_on = st.toggle("🔊 Speaking Mode", value=True)
        st.markdown("---")
        with st.expander("📚 Train Cortex"):
            u_t = st.text_input("Topic"); u_m = st.text_area("Context")
            if st.button("Submit"):
                if u_t and u_m: save_context_request(u_t, u_m, conn); st.success("Logged.")
        if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Communicate..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        response = ""
        try:
            df = conn.read(worksheet="Memory", ttl="1s")
            qs = df['question'].fillna('').tolist()
            match, score = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
            if score >= 85: response = df[df['question'] == match].iloc[-1]['answer']
        except: pass
        if not response: response = "I haven't learned that yet."
        trans = get_translation(response, st.session_state.target_lang_code) if choice != "None" else None
        full = f"{response}\n\n---\n**Translation:** {trans}" if trans else response
        with st.chat_message("assistant"):
            st.markdown(full)
            if voice_on: show_voices(response, trans, st.session_state.target_lang_code, choice)
        st.session_state.messages.append({"role": "assistant", "content": full})

#--------------------
# PAGE: BDL THINK
#--------------------
def show_bdl_deepthink():
    apply_theme("cyberpunk")
    if st.sidebar.button("⬅️ EXIT"): st.session_state.page = "Nexus Home"; st.rerun()
    st.title("🧠 BDL Think")
    with st.sidebar:
        st.session_state.deepthink_sport = st.toggle("🏃 Sport Mode", value=st.session_state.deepthink_sport)
        st.session_state.deepthink_strictness = st.slider("🔍 Strictness", 50, 100, st.session_state.deepthink_strictness)
    prompt = st.chat_input("Scan Topic...")
    if prompt:
        with st.chat_message("user"): st.markdown(prompt)
        with st.status("Scanning...", expanded=True): res = run_deepthink_engine(prompt, sport=st.session_state.deepthink_sport)
        with st.chat_message("assistant"): st.markdown(res)

#--------------------
# PAGE: BDL ONION (Synthesis Engine)
#--------------------
def show_bdl_onion():
    apply_theme("cyberpunk")
    st.title("🧅 BDL Onion")
    if st.sidebar.button("EXIT"): st.session_state.page = "Nexus Home"; st.rerun()
    prompt = st.chat_input("Peel the context...")
    if prompt:
        with st.chat_message("user"): st.markdown(prompt)
        with st.status("Synthesizing Layers...", expanded=True):
            # Restored Synthesis Logic
            try:
                ctx_df = conn.read(worksheet="Context", ttl="1s")
                topics = ctx_df['Topic'].fillna('').tolist()
                match, score = process.extractOne(prompt, topics, scorer=fuzz.token_set_ratio)
                if score >= 85:
                    raw_data = ctx_df[ctx_df['Topic'] == match].iloc[-1]['Meaning']
                    tokens = re.findall(r'\b\w{5,}\b', raw_data.lower())
                    res = f"### 🧪 ONION SYNTHESIS\n\n**Processed Layers:** {', '.join(list(set(tokens))[:5])}...\n\n{raw_data[:850]}..."
                else: res = "No matching cortex layers found for this topic."
            except: res = "Onion Cortex Offline."
        with st.chat_message("assistant"): st.markdown(res)

#--------------------
# PAGE: BDL DNA (Genealogy)
#--------------------
def show_bdl_dna_new():
    apply_theme("cyberpunk")
    st.title("🧬 BDL DNA")
    if st.sidebar.button("EXIT"): st.session_state.page = "Nexus Home"; st.rerun()
    search_target = st.text_input("Enter Name")
    if st.button("Scan DNA") and search_target:
        with st.status("Scanning Records...", expanded=True):
            wiki_wiki = wikipediaapi.Wikipedia(user_agent='BDL-AI/1.0', language='en')
            page = wiki_wiki.page(search_target)
            if page.exists():
                res = f"### 🌳 DNA TREE: {page.title}\n\n{page.summary[:800]}..."
                found = [r for r in ["born to", "married", "spouse", "children", "son", "daughter"] if r in page.text.lower()]
                res += "\n\n**Detected Connections:** " + (", ".join(found) if found else "None")
            else: res = "No records found."
        st.markdown(res)

#--------------------
# ROUTER
#--------------------
if st.session_state.page == "Nexus Home": show_nexus_home()
elif st.session_state.page == "BDL Standard": show_bdl_standard()
elif st.session_state.page == "BDL Deepthink": show_bdl_deepthink()
elif st.session_state.page == "BDL Onion": show_bdl_onion()
elif st.session_state.page == "BDL DNA New": show_bdl_dna_new()
