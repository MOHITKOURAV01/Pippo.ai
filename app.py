import streamlit as st
import os
import tempfile
import pandas as pd
import numpy as np
import base64
from src.extract import extract_text_from_pdf, extract_legal_metadata
from src.clause_splitter import split_into_clauses
from src.predict import predict_risk
from src.agent_logic import analyze_risk_with_agent
from src.exporter import generate_json_report, generate_pdf_report
from src.database import save_audit
from src.auth import auth_screen
import concurrent.futures
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import time

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pippo AI | Intelligent Legal Partner",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "guest_mode" not in st.session_state:
    st.session_state.guest_mode = False
if "show_auth" not in st.session_state:
    st.session_state.show_auth = False

# Application Gateway: Dashboard (Hero) by default
if st.session_state.show_auth and not st.session_state.authenticated:
    auth_screen()
    st.stop()

if "user_name" not in st.session_state:
    st.session_state.user_name = "User"
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None
if "metadata" not in st.session_state:
    st.session_state.metadata = None
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None
if "agent_results" not in st.session_state:
    st.session_state.agent_results = {}
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

# Listener for navbar actions via query parameters
if "action" in st.query_params:
    action = st.query_params["action"]
    if action == "login" or action == "signup":
        st.session_state.show_auth = True
    elif action == "logout":
        st.session_state.authenticated = False
        st.session_state.show_auth = False
    # Clear and rerun to ensure clean state
    # We clear to avoid re-triggering logic on back/forward or manual refresh
    params = st.query_params.to_dict()
    if "action" in params:
        del params["action"]
        st.query_params.clear()
        for k, v in params.items():
            st.query_params[k] = v
    st.rerun()

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS & DESIGN TOKENS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cabin+Sketch:wght@400;700&family=Inter:wght@300;400;500;600;700;800&family=Geist:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        /* Colors */
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
        --text-muted: rgba(255, 255, 255, 0.4);
        
        /* Spacing System */
        --space-xs: 8px;
        --space-sm: 16px;
        --space-md: 24px;
        --space-lg: 32px;
        --space-xl: 48px;
        --space-2xl: 64px;
        
        /* Layout */
        --max-width: 1400px;
        --nav-height: 72px;
        --radius-md: 12px;
        --radius-lg: 20px;
        --border-glass: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* ── Global Reset ─────────────────────────── */
    .stApp {
        background: var(--bg-black) !important;
        background-image:
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(88,166,255,0.06), transparent),
            url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
        color: var(--text-main) !important;
        font-family: 'Geist', 'Inter', sans-serif !important;
        overflow-x: hidden !important;
    }

    /* ── Hide Streamlit Chrome ────────────────── */
    [data-testid="stHeader"], header { visibility: hidden; height: 0; padding: 0; display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .block-container { 
        padding-top: var(--space-lg) !important; 
        padding-bottom: calc(var(--nav-height) + var(--space-xl)) !important; 
        max-width: var(--max-width) !important; 
    }

    /* ── Navbar Layout ────────────────────────── */
    .pippo-navbar {
        background: linear-gradient(135deg, var(--brand-pink) 0%, var(--brand-pink-dark) 100%);
        background-image: repeating-linear-gradient(45deg, rgba(255,255,255,0.05) 0px, rgba(255,255,255,0.05) 1.5px, transparent 1.5px, transparent 12px);
        width: 100%;
        height: var(--nav-height);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 clamp(var(--space-sm), 5vw, var(--space-2xl));
        border-top: 3px solid rgba(0,0,0,0.15);
        position: fixed;
        bottom: 0;
        left: 0;
        z-index: 99999;
        box-shadow: 0 -8px 32px rgba(233,30,99,0.2);
        margin: 0;
    }
    .nav-brand { display: flex; align-items: center; gap: var(--space-sm); }
    .nav-brand h1 {
        font-family: 'Cabin Sketch', cursive; font-weight: 700;
        font-size: clamp(1.8rem, 4vw, 2.6rem); color: #FFF !important; margin: 0;
        text-shadow: 2px 2px 0px rgba(0,0,0,0.1); line-height: 1;
    }
    .nav-brand .badge {
        background: rgba(255,255,255,0.15); backdrop-filter: blur(8px);
        padding: 4px 12px; border-radius: 20px;
        font-size: 0.6rem; font-weight: 700; color: #FFF;
        font-family: 'JetBrains Mono', monospace;
        border: 1px solid rgba(255,255,255,0.2);
        letter-spacing: 0.1rem;
    }
    .nav-right { display: flex; align-items: center; gap: var(--space-md); }
    .nav-status {
        background: rgba(255,255,255,0.12); padding: 6px 14px; border-radius: 50px;
        display: flex; align-items: center; gap: var(--space-xs);
        font-size: 0.65rem; font-weight: 700; color: #FFF; font-family: 'Inter';
        border: 1px solid rgba(255,255,255,0.15);
    }
    .status-dot { width: 7px; height: 7px; background: var(--brand-green); border-radius: 50%; box-shadow: 0 0 8px var(--brand-green); }
    .nav-user { display: flex; flex-direction: column; text-align: right; line-height: 1.2; color: #FFF; }
    .nav-user .label { font-size: 0.55rem; opacity: 0.7; font-weight: 700; font-family: 'JetBrains Mono'; text-transform: uppercase; letter-spacing: 0.08rem; }
    .nav-user .name { font-size: 0.85rem; font-weight: 800; font-family: 'Inter'; }
    .nav-avatar {
        width: 38px; height: 38px; background: #FFF; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.9rem; font-weight: 800; color: var(--brand-pink);
        border: 2px solid rgba(255,255,255,0.6);
    }

    /* ── Typography & Headings ────────────────── */
    .h-title {
        font-family: 'Cabin Sketch', cursive;
        font-size: clamp(2.2rem, 8vw, 4.5rem);
        font-weight: 700; line-height: 0.95;
        letter-spacing: -2px; margin-bottom: var(--space-sm);
    }
    .label-mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem; text-transform: uppercase;
        letter-spacing: 0.18rem; color: var(--brand-blue);
        margin-bottom: var(--space-xs); display: block;
    }
    .hero-subtitle {
        font-family: 'Inter'; font-size: clamp(0.9rem, 1.5vw, 1.05rem);
        color: var(--text-muted); margin-bottom: var(--space-lg);
        max-width: 580px; line-height: 1.6;
    }

    /* ── Standardized Components ───────────────── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--bg-card);
        border: var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(88,166,255,0.25) !important;
        background: rgba(88,166,255,0.04);
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.4);
    }

    .glass-container {
        background: var(--bg-glass);
        border: var(--border-glass);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        backdrop-filter: blur(12px);
        margin-bottom: var(--space-sm);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .glass-container:hover { border-color: rgba(255,255,255,0.15); }

    .bento-card {
        background: var(--bg-card);
        border: var(--border-glass);
        border-radius: var(--radius-md);
        padding: var(--space-md);
        height: 100%;
        display: flex;
        flex-direction: column;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .bento-card:hover {
        border-color: rgba(88,166,255,0.25);
        background: rgba(88,166,255,0.04);
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.4);
    }

    /* ── Dashboard Metrics ────────────────────── */
    .stat-value {
        font-family: 'Geist', sans-serif; 
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: 800; margin: var(--space-xs) 0; line-height: 1;
    }
    .stat-label {
        color: var(--text-dim); font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05rem;
        text-transform: uppercase;
    }

    /* ── Risk Indicators ───────────────────────── */
    .risk-tag {
        padding: 6px 16px; border-radius: 50px; font-size: 0.7rem;
        font-weight: 700; text-transform: uppercase; letter-spacing: 0.08rem;
        display: inline-flex; align-items: center; gap: 8px;
    }
    .risk-high { background: rgba(255,107,107,0.1); color: var(--brand-red); border: 1px solid rgba(255,107,107,0.2); }
    .risk-low { background: rgba(81,207,102,0.1); color: var(--brand-green); border: 1px solid rgba(81,207,102,0.2); }

    /* ── Agentic Engine Feedback ───────────────── */
    .agentic-panel {
        background: linear-gradient(135deg, rgba(88,166,255,0.06) 0%, rgba(139,92,246,0.04) 100%);
        border: 1px solid rgba(88,166,255,0.15);
        border-radius: var(--radius-md); 
        padding: var(--space-md); 
        margin-top: var(--space-sm);
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    }
    .agent-title {
        font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--brand-blue);
        display: flex; align-items: center; gap: var(--space-xs);
        text-transform: uppercase; letter-spacing: 0.12rem;
    }
    .agent-text { color: #C9D1D9; font-size: 1rem; line-height: 1.8; margin-top: var(--space-sm); }

    /* ── Interaction Elements ─────────────────── */
    .upload-zone {
        border: 2px dashed rgba(88,166,255,0.2); 
        border-radius: var(--radius-lg);
        padding: var(--space-lg); 
        background: rgba(88,166,255,0.015);
        transition: all 0.3s ease;
        text-align: center;
    }
    .upload-zone:hover { border-color: var(--brand-blue); background: rgba(88,166,255,0.04); }

    .stDownloadButton > button, .stButton > button {
        width: 100%;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--text-main) !important;
        border-radius: var(--radius-md) !important;
        font-weight: 600 !important;
        padding: 12px var(--space-md) !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover, .stButton > button:hover {
        background: var(--brand-blue) !important;
        color: var(--bg-black) !important;
        border-color: var(--brand-blue) !important;
        transform: translateY(-2px);
    }

    /* ── Logout Proxy Button ─────────────────── */
    .st-logout-proxy {
        position: fixed;
        bottom: 22px;
        right: clamp(20px, 10vw, 350px);
        z-index: 1000000;
        width: auto !important;
    }
    .st-logout-proxy button {
        background: rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        font-family: 'JetBrains Mono' !important;
        font-size: 0.55rem !important;
        padding: 4px 12px !important;
        color: #FFF !important;
        width: auto !important;
        min-height: 0 !important;
        height: 28px !important;
    }

    /* ── Footer ────────────────────────────────── */
    .pippo-footer {
        border-top: 1px solid rgba(255,255,255,0.08);
        padding: var(--space-lg) 0; margin-top: var(--space-2xl);
        display: flex; justify-content: space-between; align-items: center;
        flex-wrap: wrap; gap: var(--space-sm);
    }

    /* ── Responsive Refinements ────────────────── */
    @media (max-width: 1024px) {
        .block-container { padding-left: var(--space-sm) !important; padding-right: var(--space-sm) !important; }
        .st-logout-proxy { right: 20px; bottom: 80px; }
    }
    @media (max-width: 768px) {
        :root { --nav-height: 64px; --space-lg: 20px; --space-xl: 32px; }
        .pippo-navbar { height: var(--nav-height); padding: 0 var(--space-sm); }
        .nav-status, .nav-user { display: none; }
        .h-title { font-size: 2.2rem; }
        .pippo-footer { flex-direction: column; text-align: center; }
    }

    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    .fade-in { animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) both; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HELPER: Load brand image safely
# ─────────────────────────────────────────────────────────────
def get_brand_image_b64():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_dir, "assets", "Whisk_mwykjdnhjdnlfdz40iz2atotuwn4qtlxcdol1cm__1_-removebg-preview.png")
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# ─────────────────────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1.2, 1], gap="large")

with col_left:
    st.markdown("""
        <div class="fade-in">
            <div class="h-title">
                <span style="color: #58A6FF; text-shadow: 0 0 40px rgba(88,166,255,0.2);">Bharat's Precision.</span><br>
                <span style="color: #E6EDF3;">Global Ambition.</span><br>
                <span style="color: #E91E63; text-shadow: 0 0 30px rgba(233,30,99,0.2);">Intelligent</span>
                <span style="color: #E91E63; font-weight: 800;">World.</span>
            </div>
        </div>
        <p class="hero-subtitle fade-in">
            Architecture matters. While regular trackers skim the surface, Pippo AI is engineered
            for the deep nuances of Bharat's legal landscape. 🇮🇳
        </p>
    """, unsafe_allow_html=True)


    st.markdown('<span class="label-mono">Uplink Terminal</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a contract PDF for analysis", type="pdf", label_visibility="collapsed")
    if uploaded_file:
        st.markdown('<div class="risk-tag risk-low" style="text-align:center; margin-top: 8px;">✓ UPLINK SUCCESSFUL</div>', unsafe_allow_html=True)


with col_right:
    if not uploaded_file and not st.session_state.analysis_complete:
        img_b64 = get_brand_image_b64()
        if img_b64:
            st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img_b64}" style="max-width:100%; width:min(750px, 100%); height:auto; filter:drop-shadow(0 0 40px rgba(88,166,255,0.08));"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ANALYSIS PIPELINE
# ─────────────────────────────────────────────────────────────
if uploaded_file:
    need_analysis = (st.session_state.uploaded_filename != uploaded_file.name or st.session_state.processed_data is None)

    if need_analysis:
        st.session_state.agent_results = {}
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getbuffer())
            temp_path = tmp.name

        progress_placeholder = st.empty()
        with progress_placeholder.container():
            progress_bar = st.progress(0, text="Analyzing...")
            full_text = extract_text_from_pdf(temp_path)
            clause_list = split_into_clauses(full_text)
            metadata = extract_legal_metadata(full_text)
            
            def _process_clause(c):
                p = predict_risk(c)[0]
                return {"clause": c, "is_risky": p['is_risky'], "confidence": p['risk_probability']}

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                processed_data = list(executor.map(_process_clause, clause_list))
            
            progress_bar.progress(100, text="Done.")
            time.sleep(0.5)

        if os.path.exists(temp_path): os.remove(temp_path)
        st.session_state.processed_data = processed_data
        st.session_state.metadata = metadata
        st.session_state.uploaded_filename = uploaded_file.name
        st.session_state.analysis_complete = True
        progress_placeholder.empty()

    processed_data = st.session_state.processed_data
    metadata = st.session_state.metadata

    if processed_data and metadata:
        risky_count = sum(1 for x in processed_data if x['is_risky'])
        safe_count = len(processed_data) - risky_count
        integrity = int(safe_count / len(processed_data) * 100) if len(processed_data) > 0 else 0

        st.markdown('<br><span class="label-mono">Contract DNA</span>', unsafe_allow_html=True)
        meta_cols = st.columns(4)
        for i, (key, val) in enumerate(metadata.items()):
            with meta_cols[i % 4]:
                st.markdown(f'<div class="bento-card"><span class="label-mono" style="font-size:0.5rem;">{key}</span><p style="font-size:0.85rem; font-weight:600; color:#58A6FF;">{val}</p></div>', unsafe_allow_html=True)

        st.markdown('<br><span class="label-mono">Risk Analytics</span>', unsafe_allow_html=True)
        vis_col1, vis_col2 = st.columns(2)
        with vis_col1:
            with st.container(border=True):
                fig_donut = px.pie(values=[risky_count, safe_count], names=["Risky", "Safe"], hole=0.6, color_discrete_map={"Risky": "#FF6B6B", "Safe": "#51CF66"}, template="plotly_dark")
                fig_donut.update_traces(marker=dict(line_color='#000', line_width=2))
                fig_donut.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=300, margin=dict(t=20, b=20, l=10, r=10))
                st.plotly_chart(fig_donut, use_container_width=True)

        with vis_col2:
            with st.container(border=True):
                st.markdown(f'<div style="text-align:center; padding:40px;"><div class="stat-value">{integrity}%</div><p class="stat-label">SAFE RATIO</p></div>', unsafe_allow_html=True)

        st.markdown('<br><span class="label-mono">Clause Audit</span>', unsafe_allow_html=True)
        for i, item in enumerate(processed_data):
            risk_class = "risk-high" if item['is_risky'] else "risk-low"
            st.markdown(f'<div class="glass-container"><div style="display:flex; justify-content:space-between;"><span class="risk-tag {risk_class}">C-{i+1}</span><span class="label-mono">{item["confidence"]:.0%} CONF</span></div><div style="margin-top:10px; color:#C9D1D9;">{item["clause"][:500]}</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# LOGOUT & NAVBAR
# ─────────────────────────────────────────────────────────────
is_guest = not st.session_state.get('authenticated', False)

if is_guest:
    u_name = "Explore Pippo"
    u_initials = "P"
    auth_label = "PUBLIC ACCESS"
    status_color = "#8B949E"
    avatar_html = ""
else:
    u_name = st.session_state.get('user_name', 'User')
    u_initials = "".join([n[0] for n in u_name.split()])[:2].upper()
    auth_label = "SECURE"
    status_color = "var(--brand-green)"
    avatar_html = f'<div class="nav-avatar">{u_initials}</div>'

# ─────────────────────────────────────────────────────────────
# BOTTOM BAR (NAVBAR + FOOTER)
# ─────────────────────────────────────────────────────────────

# CSS for integrated navbar buttons
st.markdown("""
<style>
    .nav-btn {
        background: rgba(88,166,255,0.08);
        border: 1px solid rgba(88,166,255,0.3);
        color: #58A6FF !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        font-weight: 700;
        text-decoration: none !important;
        padding: 6px 16px;
        border-radius: 4px;
        letter-spacing: 0.05rem;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        margin-left: 10px;
    }
    .nav-btn:hover {
        background: rgba(88,166,255,0.15);
        border-color: #58A6FF;
        transform: translateY(-1px);
        box-shadow: 0 0 15px rgba(88,166,255,0.2);
    }
    .nav-btn-logout {
        border-color: rgba(255,255,255,0.15);
        color: rgba(255,255,255,0.6) !important;
    }
    .nav-btn-logout:hover {
        border-color: rgba(255,255,255,0.4);
        color: #FFF !important;
    }
</style>
""", unsafe_allow_html=True)

# Build auth segment for navbar
if is_guest:
    auth_segment = f"""
        <a href="?action=login" target="_self" class="nav-btn">LOGIN</a>
        <a href="?action=signup" target="_self" class="nav-btn">SIGN UP</a>
    """
else:
    auth_segment = f"""
        <div class="nav-user">
            <span class="label">User</span>
            <span class="name">{u_name}</span>
        </div>
        {avatar_html}
        <a href="?action=logout" target="_self" class="nav-btn nav-btn-logout">OFFLINE</a>
    """

# Render combined bar (Footer + Navbar)
footer_html = f'<div class="pippo-footer"><span class="label-mono">PIPPO AI</span><span class="label-mono" style="opacity:0.2;">SYSTEM NOMINAL // V2.1.0</span></div>'
navbar_html = f'<div class="pippo-navbar"><div class="nav-brand"><h1>Pippo</h1><span class="badge">AI LEGAL</span></div><div class="nav-right"><div class="nav-status"><span class="status-dot" style="background:{status_color}"></span><span>{auth_label}</span></div>{auth_segment}</div></div>'

st.markdown(f'<div id="pippo-fixed-bottom-bar">{footer_html}{navbar_html}</div>', unsafe_allow_html=True)