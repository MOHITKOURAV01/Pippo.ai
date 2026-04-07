import os
import json
import time # Added this
import streamlit as st

# MOCK FIREBASE FOR NOW (to avoid project key errors)
# This module is structured so you can easily swap it for real Firebase logic later.

USER_DB = "data/users.json"

def init_auth():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(USER_DB):
        with open(USER_DB, "w") as f:
            json.dump({}, f)

def register_user(email, password, name):
    init_auth()
    with open(USER_DB, "r") as f:
        users = json.load(f)
    
    if email in users:
        return False, "User already exists!"
    
    users[email] = {
        "password": password,
        "name": name,
        "role": "Lawyer"
    }
    
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)
    
    return True, "Signup Successful!"

def login_user(email, password):
    init_auth()
    with open(USER_DB, "r") as f:
        users = json.load(f)
    
    if email in users and users[email]["password"] == password:
        return True, users[email]
    
    return False, "Invalid Credentials"

def auth_screen():
    """Art-form Authentication UI: Synchronized Cyber-Legal Aesthetic."""
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cabin+Sketch:wght@400;700&family=Inter:wght@300;400;500;600;700;800&family=Geist:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        :root {
            --brand-pink: #E91E63;
            --brand-pink-dark: #C2185B;
            --brand-blue: #58A6FF;
            --brand-green: #51CF66;
            --brand-red: #FF6B6B;
            --bg-black: #000000;
            --bg-glass: rgba(255, 255, 255, 0.03);
            --bg-card: rgba(255, 255, 255, 0.05);
            --text-main: #E6EDF3;
            --text-dim: #8B949E;
            --radius-md: 12px;
            --radius-lg: 20px;
            --border-glass: 1px solid rgba(255, 255, 255, 0.08);
        }

        /* Immersive Background matching Dashboard */
        .stApp {
            background-color: var(--bg-black) !important;
            background-image: 
                radial-gradient(at 0% 0%, hsla(328,100%,7%,1) 0, transparent 50%), 
                radial-gradient(at 100% 0%, hsla(225,100%,5%,1) 0, transparent 50%),
                url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E") !important;
            background-attachment: fixed !important;
            color: var(--text-main) !important;
            font-family: 'Geist', 'Inter', sans-serif !important;
        }

        .auth-container {
            max-width: 480px;
            margin: 0 auto;
            padding-top: 80px;
        }

        .auth-card {
            background: var(--bg-card);
            border: var(--border-glass);
            backdrop-filter: blur(25px);
            border-radius: var(--radius-lg);
            padding: 40px;
            box-shadow: 0 40px 100px rgba(0,0,0,0.5);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .auth-card:hover {
            border-color: rgba(88,166,255,0.2);
            background: rgba(88,166,255,0.02);
        }

        .logo-text {
            font-family: 'Cabin Sketch', cursive;
            font-size: 4.5rem;
            font-weight: 700;
            color: #FFF;
            margin-bottom: 5px;
            letter-spacing: -2px;
            text-shadow: 0 0 30px rgba(233,30,99,0.3);
            text-align: center;
        }

        .protocol-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.6rem;
            letter-spacing: 0.15rem;
            color: var(--brand-blue);
            text-transform: uppercase;
            text-align: center;
            margin-bottom: 40px;
            opacity: 0.8;
        }

        /* Modernized Inputs */
        div[data-baseweb="input"] {
            background: rgba(255,255,255,0.02) !important;
            border-radius: var(--radius-md) !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            transition: all 0.3s ease !important;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: var(--brand-blue) !important;
            background: rgba(88,166,255,0.05) !important;
            box-shadow: 0 0 15px rgba(88,166,255,0.1) !important;
        }

        /* Buttons matching Dashboard */
        div.stButton > button {
            background: linear-gradient(135deg, var(--brand-pink) 0%, var(--brand-pink-dark) 100%) !important;
            border: none !important;
            color: white !important;
            font-weight: 700 !important;
            letter-spacing: 0.05rem !important;
            text-transform: uppercase !important;
            padding: 12px !important;
            border-radius: var(--radius-md) !important;
            box-shadow: 0 10px 20px rgba(233,30,99,0.2) !important;
            transition: all 0.3s ease !important;
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 15px 30px rgba(233,30,99,0.4) !important;
            filter: brightness(1.1);
        }

        .stRadio div[role="radiogroup"] {
            justify-content: center !important;
            padding-bottom: 15px !important;
            margin-bottom: 25px !important;
            border-bottom: 1px solid rgba(255,255,255,0.05) !important;
        }
        
        .label-mono {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.55rem;
            text-transform: uppercase;
            letter-spacing: 0.1rem;
            color: var(--text-dim);
            margin-bottom: 8px;
            display: block;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown('<div class="logo-text">Pippo</div>', unsafe_allow_html=True)
        st.markdown('<div class="protocol-label">// NEURAL LEGAL INTERFACE V2.1</div>', unsafe_allow_html=True)
        
        mode = st.radio("VAULT_ACCESS", ["UPLINK", "REGISTER"], horizontal=True, label_visibility="collapsed")
        
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        if mode == "UPLINK":

            email = st.text_input("NODE_ADDRESS", placeholder="lawyer@pippo.ai")
            password = st.text_input("VAULT_KEY", type="password", placeholder="••••••••")
            st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
            if st.button("AUTHENTICATE_SESSION", use_container_width=True):
                success, user_data = login_user(email, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_name = user_data["name"]
                    st.rerun()
                else:
                    st.error(f"CORRUPTION: {user_data}")
        else:

            name = st.text_input("AGENT_NAME", placeholder="Enter your name")
            email = st.text_input("UPLINK_EMAIL", placeholder="lawyer@pippo.ai")
            password = st.text_input("GENERATED_VAULT_KEY", type="password", placeholder="••••••••")
            st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
            if st.button("INITIALIZE_AGENT", use_container_width=True):
                if name and email and password:
                    success, msg = register_user(email, password, name)
                    if success:
                        st.success(f"SUCCESS: {msg}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"REJECTION: {msg}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Back to Dashboard Bypass
        st.markdown('<div style="text-align:center; margin-top:25px;">', unsafe_allow_html=True)
        if st.button("BACK TO HERO_SECTION", key="guest_bypass", help="Return to the main dashboard"):
            st.session_state.show_auth = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
