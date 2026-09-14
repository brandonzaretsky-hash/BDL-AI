import streamlit as st
import sqlite3

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="BDL HUB", layout="wide", page_icon="⚡")

# --- 2. SQLITE DATABASE SETUP ---
DB_FILE = "bdl_users.db"

def init_db():
    """Creates the SQLite database and seeds root SuperAdmin account."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    # Seed default SuperAdmin if missing
    c.execute("SELECT * FROM users WHERE username = 'Brandon'")
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES ('Brandon', '0809', 'SuperAdmin')")
    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    res = c.fetchone()
    conn.close()
    return res[0] if res else None

def register_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, 'User')", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, role FROM users")
    users = c.fetchall()
    conn.close()
    return users

def update_role(username, new_role):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
    conn.commit()
    conn.close()

init_db()

# --- 3. SESSION STATE INITIALIZATION ---
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = "Free"
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Hub"

# --- 4. MIDNIGHT DARK (EYE-FRIENDLY) CSS ---
def apply_styles():
    st.markdown("""
        <style>
        /* Base Background & Body Text */
        .stApp {
            background-color: #0f141d;
            color: #d0d7e5;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        /* Softer Headings */
        h1, h2, h3 {
            color: #e2e8f0 !important;
            text-align: center;
            font-weight: 600;
        }

        h1 {
            color: #818cf8 !important;
        }
        
        /* Card Container Base */
        .card-container {
            position: relative;
            background: #182030;
            border: 1px solid #2d3748;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            margin-bottom: 20px;
        }

        /* Subdued Caution Tape Overlay */
        .caution-overlay {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: repeating-linear-gradient(
                45deg,
                rgba(217, 119, 6, 0.25),
                rgba(217, 119, 6, 0.25) 15px,
                rgba(15, 20, 29, 0.6) 15px,
                rgba(15, 20, 29, 0.6) 30px
            );
            z-index: 1;
        }

        .caution-banner {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-6deg);
            background: #b45309;
            color: #fef3c7;
            font-weight: 600;
            font-size: 1.05rem;
            padding: 6px 24px;
            border: 1px solid #78350f;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
            z-index: 2;
            white-space: nowrap;
        }

        .card-content {
            z-index: 0;
            filter: blur(2.5px);
            opacity: 0.6;
        }

        /* Buttons Styling */
        .stButton>button {
            background-color: #1e293b;
            color: #94a3b8;
            border: 1px solid #334155;
            border-radius: 8px;
            width: 100%;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            border-color: #6366f1;
            color: #e0e7ff;
            background-color: #312e81;
        }

        /* Sidebar Customization */
        section[data-testid="stSidebar"] {
            background-color: #111827;
            border-right: 1px solid #1f2937;
        }
        </style>
    """, unsafe_allow_html=True)

apply_styles()

# --- 5. SIDEBAR AUTH & ADMIN MANAGEMENT ---
with st.sidebar:
    st.title("🛡️ Access Panel")
    
    if st.button("🌐 RETURN TO HUB"):
        st.session_state.current_mode = "Hub"
        st.rerun()

    st.markdown("---")

    if st.session_state.user:
        st.success(f"Logged in as: **{st.session_state.user}**")
        st.caption(f"Role: **{st.session_state.role}**")
        if st.button("🚪 Log Out"):
            st.session_state.user = None
            st.session_state.role = "Free"
            st.session_state.current_mode = "Hub"
            st.rerun()
    else:
        st.subheader("Login / Sign Up")
        tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])
        
        with tab_login:
            login_user = st.text_input("Username", key="login_u")
            login_pass = st.text_input("Password", type="password", key="login_p")
            if st.button("Log In"):
                role = authenticate(login_user, login_pass)
                if role:
                    st.session_state.user = login_user
                    st.session_state.role = role
                    st.success("Authenticated!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

        with tab_signup:
            signup_user = st.text_input("New Username", key="sign_u")
            signup_pass = st.text_input("New Password", type="password", key="sign_p")
            if st.button("Create Account"):
                if signup_user and signup_pass:
                    if register_user(signup_user, signup_pass):
                        st.success("Account created! Please Log In.")
                    else:
                        st.error("Username taken.")
                else:
                    st.warning("Fill out all fields.")

    # SUPERADMIN & ADMIN SIDEBAR PANEL
    if st.session_state.role in ["Admin", "SuperAdmin"]:
        st.markdown("---")
        st.subheader("👑 Admin User Deck")
        all_users = get_all_users()
        
        for u, r in all_users:
            if u == "Brandon":
                continue
            st.write(f"👤 **{u}** ({r})")
            if st.session_state.user == "Brandon":
                c1, c2 = st.columns(2)
                if r != "Admin" and c1.button("Make Admin", key=f"mk_{u}"):
                    update_role(u, "Admin")
                    st.rerun()
                if r == "Admin" and c2.button("Revoke Admin", key=f"rm_{u}"):
                    update_role(u, "User")
                    st.rerun()

# --- 6. ROUTING ENGINE & HUB LAYOUT ---

def attempt_entry(mode_name, is_locked):
    """Enforces role access logic for locked and active modes."""
    is_admin = st.session_state.role in ["Admin", "SuperAdmin"]
    
    if is_locked and not is_admin:
        st.error(f"⛔ Access Denied. '{mode_name}' is locked under development. Only Admins can bypass caution tape.")
    else:
        st.session_state.current_mode = mode_name
        st.rerun()

# --- PAGE: BDL HUB ---
if st.session_state.current_mode == "Hub":
    st.title("BDL HUB")
    st.caption("Central Gateway | Select a Module System")

    is_admin_user = st.session_state.role in ["Admin", "SuperAdmin"]
    prefix = "Enter " if is_admin_user else ""

    # Row 1: 4 Cards
    col1, col2, col3, col4 = st.columns(4)
    
    # 1. Picture-Rama
    with col1:
        st.markdown("""
            <div class='card-container'>
                <div class='caution-overlay'></div>
                <div class='caution-banner'>COMING SOON</div>
                <div class='card-content'>
                    <div style='font-size: 50px;'>📷</div>
                    <h3>Picture-Rama</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{prefix}Picture-Rama", key="btn_pr"):
            attempt_entry("Picture-Rama", is_locked=True)

    # 2. The Brain
    with col2:
        st.markdown("""
            <div class='card-container'>
                <div class='caution-overlay'></div>
                <div class='caution-banner'>COMING SOON</div>
                <div class='card-content'>
                    <div style='font-size: 50px;'>🧠</div>
                    <h3>The Brain</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{prefix}The Brain", key="btn_tb"):
            attempt_entry("The Brain", is_locked=True)

    # 3. Crowd Brain
    with col3:
        st.markdown("""
            <div class='card-container'>
                <div class='caution-overlay'></div>
                <div class='caution-banner'>COMING SOON</div>
                <div class='card-content'>
                    <div style='font-size: 50px;'>👥</div>
                    <h3>Crowd Brain</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{prefix}Crowd Brain", key="btn_cb"):
            attempt_entry("Crowd Brain", is_locked=True)

    # 4. The Code
    with col4:
        st.markdown("""
            <div class='card-container'>
                <div class='caution-overlay'></div>
                <div class='caution-banner'>COMING SOON</div>
                <div class='card-content'>
                    <div style='font-size: 50px;'>💻</div>
                    <h3>The Code</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{prefix}The Code", key="btn_tc"):
            attempt_entry("The Code", is_locked=True)

    st.markdown("---")

    # Row 2: Wiki-Brain
    col_w1, col_w2, col_w3 = st.columns([1, 2, 1])
    with col_w2:
        st.markdown("""
            <div class='card-container'>
                <div class='caution-overlay'></div>
                <div class='caution-banner'>COMING SOON</div>
                <div class='card-content'>
                    <div style='font-size: 50px;'>📖</div>
                    <h3>Wiki-Brain</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{prefix}Wiki-Brain", key="btn_wb"):
            attempt_entry("Wiki-Brain", is_locked=True)

# --- MODULE PLACEHOLDER VIEWS (ADMIN UNLOCKED MODE) ---
else:
    st.title(f"⚡ {st.session_state.current_mode}")
    st.warning("⚠️ Admin Override Active: You have bypassed the Caution Tape overlay.")
    st.info(f"Welcome to the internal module environment for **{st.session_state.current_mode}**.")
    
    if st.button("Return to BDL Hub"):
        st.session_state.current_mode = "Hub"
        st.rerun()
