import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import base64

#--------------------
# PAGE CONFIGURATION
#--------------------
st.set_page_config(page_title="BDL.AI - Master Brain", page_icon="🧠", layout="wide")

#--------------------
# CUSTOM CSS & ANIMATIONS
#--------------------
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    h1 { color: #00d4ff; text-align: center; text-shadow: 0 0 10px #00d4ff; }
    .pulse-container { display: flex; align-items: center; gap: 10px; font-weight: bold; color: #00ff00; margin-bottom: 20px; }
    .pulse-circle {
        width: 12px; height: 12px; background-color: #00ff00; border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

#--------------------
# INITIALIZE SESSION STATE
#--------------------
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""
if "messages" not in st.session_state: st.session_state.messages = []

#--------------------
# GOOGLE SHEETS CONNECTION
#--------------------
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    connection_status = "Online"
except Exception:
    connection_status = "Offline"
    st.stop()

def load_brain_data():
    return conn.read(ttl=0)

#--------------------
# SIDEBAR & ADMIN DASHBOARD
#--------------------
with st.sidebar:
    st.title("🔐 Master Control")
    password_input = st.text_input("Admin Key", type="password")
    
    # 1. ADMIN CHECK
    if password_input == "admin123":
        st.session_state.is_admin = True
        st.markdown('<div class="pulse-container"><div class="pulse-circle"></div><span>ADMIN: ONLINE</span></div>', unsafe_allow_html=True)
        
        # Load data for analytics
        df = load_brain_data()
        
        # --- FEATURE 1: PENDING REVIEW ---
        pending_df = df[df['status'] == 'pending'] if 'status' in df.columns else pd.DataFrame()
        if not pending_df.empty:
            st.warning(f"🔔 {len(pending_df)} New Requests!")
            st.components.v1.html("<audio autoplay><source src='https://www.soundjay.com/buttons/sounds/button-3.mp3'></audio>", height=0)
            
            st.markdown("### 📝 Pending Review")
            for index, row in pending_df.iterrows():
                with st.expander(f"Q: {row['question'][:15]}..."):
                    st.write(f"**A:** {row['answer']}")
                    col1, col2 = st.columns(2)
                    if col1.button("✅", key=f"app_{index}"):
                        df.at[index, 'status'] = 'verified'
                        conn.update(data=df)
                        st.rerun()
                    if col2.button("🗑️", key=f"del_{index}"):
                        conn.update(data=df.drop(index))
                        st.rerun()

        # --- FEATURE 2: BRAIN ANALYTICS ---
        st.markdown("---")
        st.markdown("### 📊 Brain Growth")
        if not df.empty and 'timestamp' in df.columns:
            # Clean and prepare date data
            df['date_only'] = pd.to_datetime(df['timestamp']).dt.date
            growth_data = df.groupby('date_only').size().reset_index(name='Memories')
            st.bar_chart(growth_data.set_index('Date_only' if 'Date_only' in growth_data else 'date_only'), color="#00d4ff")
            
            # Quick Stats
            st.write(f"🧠 Total Size: **{len(df)}**")
        
        # --- FEATURE 3: WORD CLOUD ---
        st.markdown("---")
        st.markdown("### ☁️ Common Topics")
        if not df.empty:
            all_text = " ".join(df['question'].astype(str)).lower()
            # Simple word frequency (top 5 words)
            words = pd.Series(all_text.split()).value_counts().head(5)
            for word, count in words.items():
                st.write(f"**{word}** ({count}x)")

    # 2. USER MODE (If no password)
    else:
        st.session_state.is_admin = False
        st.info("User Mode: Suggestions will be sent to Admin.")
        
    st.markdown("---")
    if st.button("Clear Visual Chat"):
        st.session_state.messages = []
        st.rerun()
#--------------------
# BRAIN ANALYTICS (ADMIN ONLY)
#--------------------
st.markdown("---")
st.markdown("### 📊 Brain Growth")

if not df.empty and 'timestamp' in df.columns:
    # 1. Convert timestamp column to actual dates
    df['date_only'] = pd.to_datetime(df['timestamp']).dt.date
    
    # 2. Count how many entries per day
    growth_data = df.groupby('date_only').size().reset_index(name='New Memories')
    
    # 3. Rename columns for the chart
    growth_data.columns = ['Date', 'Memories']
    
    # 4. Display the Chart
    st.bar_chart(growth_data.set_index('Date'), color="#00d4ff")
    
    # 5. Quick Stats
    total_memories = len(df)
    verified_memories = len(df[df['status'] == 'verified'])
    st.write(f"Total Brain Size: **{total_memories}**")
    st.write(f"Verified Knowledge: **{verified_memories}**")
else:
    st.info("No analytics data available yet. Start teaching BDL!")

#--------------------
# MAIN UI
#--------------------
st.title("🧠 BDL.AI - Master Brain")
st.caption("v2.5 - Admin Dashboard & Moderation Engine")

for message in st.session_state.messages:
    with st.chat_message(message["role"]): st.markdown(message["content"])

#--------------------
# THE MASTER BRAIN LOGIC
#--------------------
if prompt := st.chat_input("Ask BDL..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    response = ""

    # --- MATH CALCULATOR ---
    import re
    if re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", prompt.strip()):
        try: response = f"🔢 **Result:** {pd.eval(prompt)}"
        except: pass

    # --- FORGET (ADMIN ONLY) ---
    if not response and prompt.lower().strip() == "forget that":
        if st.session_state.is_admin:
            df = load_brain_data()
            if not df.empty:
                last_q = df.iloc[-1]['question']
                conn.update(data=df.drop(df.tail(1).index))
                response = f"🗑️ **Forgotten:** '{last_q}'"
        else: response = "🚫 Admin access required."

    # --- LEARNING & METADATA (FEATURE 3) ---
    elif not response and st.session_state.waiting_for_answer:
        df = load_brain_data()
        status = "verified" if st.session_state.is_admin else "pending"
        # Adding Timestamp (Metadata)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_row = pd.DataFrame([{
            "question": st.session_state.last_question.lower(), 
            "answer": prompt, 
            "status": status,
            "timestamp": now # Feature 3: Records when it happened
        }])
        
        conn.update(data=pd.concat([df, new_row], ignore_index=True))
        response = "✅ Learned!" if st.session_state.is_admin else "📩 Suggestion saved for Admin review."
        st.session_state.waiting_for_answer = False

    # --- SMART RETRIEVAL ---
    elif not response:
        from thefuzz import process, fuzz
        df = load_brain_data()
        verified_df = df[df['status'] == 'verified'] if 'status' in df.columns else df
        questions = verified_df['question'].fillna('').tolist()
        
        if questions:
            best_match, score = process.extractOne(prompt, questions, scorer=fuzz.token_sort_ratio)
            if score >= 80:
                response = verified_df[verified_df['question'] == best_match].iloc[0]['answer']
        
        if not response:
            response = "I don't know that. **What should the answer be?**"
            st.session_state.waiting_for_answer = True
            st.session_state.last_question = prompt

    with st.chat_message("assistant"): st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


