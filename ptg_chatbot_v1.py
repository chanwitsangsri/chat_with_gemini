"""
PTG AI Advisor — Streamlit Chatbot
====================================
Matches the Figma design: AI Retailer Advisor / AI Landlord Advisor page.

Run:
    pip install streamlit supabase google-genai pandas
    streamlit run ptg_chatbot.py
"""

import json
import textwrap
import streamlit as st
import pandas as pd
from google import genai
from supabase import create_client, Client

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG — loaded from .streamlit/secrets.toml
# ══════════════════════════════════════════════════════════════════════════════

def _load_secrets():
    required = ["SUPABASE_URL", "SUPABASE_KEY", "GEMINI_API_KEY"]
    missing  = [k for k in required if k not in st.secrets]
    if missing:
        st.error(f"❌ Missing secrets: {', '.join(missing)}. Add them to .streamlit/secrets.toml")
        st.stop()

    url = st.secrets["SUPABASE_URL"]
    if not url.startswith("https://"):
        st.error("❌ SUPABASE_URL must start with https:// — check your secrets.toml")
        st.stop()

    return (
        url,
        st.secrets["SUPABASE_KEY"],
        st.secrets["GEMINI_API_KEY"],
        st.secrets.get("GEMINI_MODEL", "gemini-3.1-flash-lite-preview"),
    )

SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY, GEMINI_MODEL = _load_secrets()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="PTG AI Advisor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS — matches Figma exactly
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:wght@400;700&family=Manrope:wght@400;500;700&display=swap');

/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #FAFAF3 !important;
    font-family: 'Manrope', sans-serif;
}

/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #FAFAF9 !important;
    border-right: 1px solid rgba(231,229,228,0.5) !important;
    width: 256px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

.sidebar-brand {
    padding: 24px 24px 8px 24px;
}
.sidebar-brand-title {
    font-family: 'Newsreader', serif;
    font-size: 24px;
    font-weight: 800;
    color: #1C1917;
    line-height: 32px;
}
.sidebar-brand-sub {
    font-family: 'Manrope', sans-serif;
    font-size: 10px;
    font-weight: 400;
    color: #A8A29E;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 2px;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    margin: 2px 16px;
    border-radius: 8px;
    font-family: 'Manrope', sans-serif;
    font-size: 16px;
    font-weight: 400;
    color: #57534E;
    cursor: pointer;
    text-decoration: none;
}
.nav-link:hover { background: rgba(231,229,228,0.3); }
.nav-link.active {
    background: #F7FEE7;
    border-right: 4px solid #65A30D;
    color: #84BD25;
    font-weight: 600;
    border-radius: 8px 0 0 8px;
}

.sidebar-user {
    margin: 0 16px;
    padding: 16px;
    border-top: 1px solid #F5F5F4;
    display: flex;
    align-items: center;
    gap: 12px;
}
.sidebar-avatar {
    width: 40px; height: 40px;
    background: #84BD25;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 14px; color: white;
    flex-shrink: 0;
}
.sidebar-user-name { font-weight: 700; font-size: 14px; color: #1A1C18; }
.sidebar-user-role { font-size: 12px; color: #A8A29E; }

/* ── Main content area ── */
.main-content {
    padding: 80px 48px 48px 48px;
    max-width: 960px;
}

/* ── Page title ── */
.page-title {
    font-family: 'Newsreader', serif;
    font-size: 48px;
    font-weight: 400;
    color: #1A1C18;
    margin-bottom: 32px;
    line-height: 1;
}

/* ── Bento hero cards ── */
.bento-row {
    display: grid;
    grid-template-columns: 1fr 380px;
    gap: 24px;
    margin-bottom: 40px;
}

.hero-card-left {
    background: #FFFFFF;
    border: 1px solid rgba(245,245,244,0.5);
    box-shadow: 0px 1px 2px rgba(0,0,0,0.05);
    border-radius: 32px;
    padding: 40px;
}

.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(214,234,174,0.3);
    border-radius: 9999px;
    padding: 4px 12px;
    margin-bottom: 16px;
}
.live-dot {
    width: 8px; height: 8px;
    background: #84BD25;
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.live-text {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #446900;
}
.hero-headline {
    font-family: 'Newsreader', serif;
    font-size: 28px;
    font-weight: 400;
    color: #1A1C18;
    line-height: 1.4;
    margin-bottom: 24px;
}
.hero-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    border-top: 1px solid #F5F5F4;
    padding-top: 20px;
}
.hero-stat-label {
    font-size: 11px;
    font-weight: 400;
    color: #A8A29E;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}
.hero-stat-value {
    font-family: 'Newsreader', serif;
    font-size: 40px;
    font-weight: 700;
    color: #1A1C18;
}
.hero-stat-value.green { color: #446900; }

.hero-card-right {
    background: #446900;
    border-radius: 32px;
    padding: 40px;
    position: relative;
    overflow: hidden;
}
.hero-card-right::after {
    content: '';
    position: absolute;
    width: 192px; height: 192px;
    right: -40px; bottom: -40px;
    background: rgba(132,189,37,0.2);
    filter: blur(32px);
    border-radius: 50%;
}
.forecast-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.6);
    margin-bottom: 8px;
}
.forecast-title {
    font-family: 'Newsreader', serif;
    font-size: 24px;
    color: #FFFFFF;
    line-height: 1.3;
    margin-bottom: 12px;
}
.forecast-body {
    font-size: 14px;
    color: #B8F55A;
    line-height: 1.6;
    margin-bottom: 20px;
}
.forecast-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #84BD25;
    color: #2E4800;
    font-weight: 700;
    font-size: 14px;
    padding: 12px 24px;
    border-radius: 9999px;
    cursor: pointer;
    border: none;
    position: relative;
    z-index: 1;
}

/* ── Recommendation cards ── */
.rec-section-title {
    font-family: 'Newsreader', serif;
    font-size: 28px;
    color: #1A1C18;
    margin-bottom: 20px;
}
.rec-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 40px;
}
.rec-card {
    background: #F4F4ED;
    border-radius: 24px;
    padding: 28px;
}
.rec-icon-wrap {
    width: 48px; height: 48px;
    background: white;
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    font-size: 22px;
    margin-bottom: 16px;
}
.rec-card-title {
    font-family: 'Newsreader', serif;
    font-size: 18px;
    color: #1A1C18;
    margin-bottom: 8px;
    line-height: 1.4;
}
.rec-card-body {
    font-size: 13px;
    color: #78716C;
    line-height: 1.65;
    margin-bottom: 12px;
}
.rec-tag {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
}
.rec-tag.green { color: #84BD25; }
.rec-tag.grey  { color: #A8A29E; }
.rec-tag.dark  { color: #446900; }

/* ── Chat section ── */
.chat-section {
    background: rgba(227,227,220,0.5);
    border: 1px solid rgba(231,229,228,0.3);
    border-radius: 40px;
    padding: 32px;
    margin-bottom: 24px;
}

/* Chat messages */
.chat-messages {
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding-right: 4px;
}
.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-track { background: transparent; }
.chat-messages::-webkit-scrollbar-thumb { background: #D6D3D1; border-radius: 2px; }

.msg-row { display: flex; gap: 12px; align-items: flex-start; }
.msg-row.user { flex-direction: row-reverse; }

.msg-avatar {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 700; flex-shrink: 0;
}
.msg-avatar.ai   { background: #446900; color: white; }
.msg-avatar.user { background: #84BD25; color: #2E4800; }

.msg-bubble {
    max-width: 75%;
    padding: 14px 18px;
    border-radius: 20px;
    font-size: 14px;
    line-height: 1.65;
}
.msg-bubble.ai {
    background: #FFFFFF;
    color: #1A1C18;
    border-bottom-left-radius: 4px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.msg-bubble.user {
    background: #446900;
    color: white;
    border-bottom-right-radius: 4px;
}

/* Suggestion chips */
.chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
}
.chip {
    background: #FFFFFF;
    border: 1px solid #F5F5F4;
    border-radius: 9999px;
    padding: 7px 16px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #78716C;
    cursor: pointer;
    transition: all 0.15s;
}
.chip:hover { background: #F4F4ED; border-color: #D6D3D1; }

/* ── Streamlit widget overrides ── */
[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    border: 1px solid rgba(231,229,228,0.4) !important;
    border-radius: 40px !important;
    padding: 20px 60px 20px 24px !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 16px !important;
    color: #1A1C18 !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #84BD25 !important;
    box-shadow: 0 0 0 3px rgba(132,189,37,0.15) !important;
}
[data-testid="stTextInput"] input::placeholder { color: #A8A29E !important; }

/* send button */
[data-testid="stButton"] > button {
    background: #84BD25 !important;
    color: #2E4800 !important;
    border: none !important;
    border-radius: 9999px !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 12px 28px !important;
    transition: background 0.2s !important;
}
[data-testid="stButton"] > button:hover { background: #6fa31e !important; }

/* selectbox */
[data-testid="stSelectbox"] > div > div {
    background: rgba(132,189,37,0.12) !important;
    border: none !important;
    border-radius: 9999px !important;
    font-family: 'Manrope', sans-serif !important;
}

/* role toggle buttons */
.role-btn-row { display: flex; gap: 12px; margin-bottom: 12px; }

/* typing indicator */
.typing { display: flex; align-items: center; gap: 6px; padding: 14px 18px; }
.typing span {
    width: 8px; height: 8px;
    background: #A8A29E; border-radius: 50%;
    animation: bounce 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-6px); }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# INIT CLIENTS (cached)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_clients():
    try:
        g = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"❌ Gemini init failed: {e}")
        st.stop()
    try:
        s = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ Supabase init failed. Check SUPABASE_URL in secrets.toml.\nError: {e}")
        st.stop()
    return g, s

gemini_client, supabase_client = get_clients()


# ══════════════════════════════════════════════════════════════════════════════
# SUPABASE FETCH FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def _fmt(data, label):
    if not data:
        return f"### {label}\n[No data]\n\n"
    if isinstance(data, dict):
        return f"### {label}\n" + "\n".join(f"  {k}: {v}" for k, v in data.items()) + "\n\n"
    return f"### {label}\n{pd.DataFrame(data).to_string(index=False)}\n\n"


def fetch_retailer(rid):
    res = supabase_client.table("retailers").select(
        "retailer_id,business_name,business_type_id,description,"
        "years_of_experience,existing_store_count,"
        "monthly_budget_min_thb,monthly_budget_max_thb,"
        "preferred_store_size,lease_duration_pref,"
        "target_demographics,data_quality_score,platform_ranking_pct"
    ).eq("retailer_id", rid).execute()
    return res.data[0] if res.data else None

def fetch_applications(rid):
    return supabase_client.table("applications").select(
        "application_id,unit_id,station_id,status,"
        "ai_match_score,ai_success_score,"
        "est_revenue_thb_mo,est_foot_traffic_pct,"
        "financial_health_score,applied_at,decision_at"
    ).eq("retailer_id", rid).execute().data

def fetch_forecast(rid):
    return supabase_client.table("ml_forecast_features").select(
        "station_id,forecast_month,actual_revenue_thb,forecast_revenue_thb,"
        "forecast_low_thb,forecast_high_thb,model_confidence_pct,"
        "mom_growth_lag1,revenue_3mo_avg_thb,"
        "daily_customers_lag1,repeat_visit_rate_lag1_pct,regional_velocity_score"
    ).eq("retailer_id", rid).order("forecast_month", desc=True).limit(12).execute().data

def fetch_ml_match(rid):
    return supabase_client.table("ml_matching_features").select(
        "application_id,station_id,match_score_label,budget_fit_ratio,"
        "demographic_overlap_score,location_type_match,"
        "avg_daily_customers,avg_dwell_time_min,"
        "unit_visibility_score,nearby_transit_flag"
    ).eq("retailer_id", rid).execute().data

def fetch_ml_success(rid):
    return supabase_client.table("ml_success_features").select(
        "application_id,station_id,success_label,"
        "financial_health_score,data_quality_score,"
        "platform_ranking_pct,demographic_overlap_score,"
        "budget_fit_ratio,lease_duration_mos,est_revenue_thb_mo"
    ).eq("retailer_id", rid).execute().data

def fetch_stations(sid=None):
    q = supabase_client.table("stations").select(
        "station_id,station_name,zone,station_type,"
        "avg_daily_customers,avg_dwell_time_min,"
        "ev_charging_points,nearby_transit,operational_status,"
        "catchment_population,ai_match_score_avg"
    )
    if sid:
        q = q.eq("station_id", sid)
    return q.execute().data

def fetch_units(sid=None):
    q = supabase_client.table("units").select(
        "unit_id,station_id,unit_reference,unit_type,"
        "floor_area_sqm,monthly_rent_thb,availability_status,"
        "zone,visibility_score"
    )
    if sid:
        q = q.eq("station_id", sid)
    return q.execute().data

def fetch_station_apps(sid):
    return supabase_client.table("applications").select(
        "application_id,retailer_id,unit_id,status,"
        "ai_match_score,ai_success_score,"
        "est_revenue_thb_mo,est_foot_traffic_pct,financial_health_score"
    ).eq("station_id", sid).order("ai_match_score", desc=True).execute().data

def fetch_ml_outputs(app_ids):
    if not app_ids:
        return []
    return supabase_client.table("ml_outputs").select(
        "output_id,model_type,ref_id,score,score_label,model_accuracy"
    ).in_("ref_id", app_ids).execute().data


@st.cache_data(ttl=300, show_spinner=False)
def build_context(role, user_id, question):
    """Cached for 5 min — same user+role+intent won't re-hit Supabase."""
    q = question.lower()
    loc_kw = ["which station","match","location","expand","new station","where should","best station","find"]
    is_loc = any(k in q for k in loc_kw)

    if role == "retailer":
        if is_loc:
            retailer = fetch_retailer(user_id)
            stations = fetch_stations()
            ml_match = fetch_ml_match(user_id)
            units    = fetch_units()
            return (
                "=== DATABASE CONTEXT ===\n\n"
                + _fmt(retailer,  "Retailer Profile")
                + _fmt(stations,  "All PTG Stations")
                + _fmt(units,     "Available Units")
                + _fmt(ml_match,  "AI Match Scores")
            )
        else:
            retailer   = fetch_retailer(user_id)
            apps       = fetch_applications(user_id)
            forecast   = fetch_forecast(user_id)
            ml_match   = fetch_ml_match(user_id)
            ml_success = fetch_ml_success(user_id)
            return (
                "=== DATABASE CONTEXT ===\n\n"
                + _fmt(retailer,   "Retailer Profile")
                + _fmt(apps,       "Applications")
                + _fmt(forecast,   "Revenue Forecast (last 12 months)")
                + _fmt(ml_match,   "AI Match Scores")
                + _fmt(ml_success, "AI Success Scores")
            )
    else:  # landlord
        sid      = user_id if user_id.startswith("STN-") else None
        stations = fetch_stations(sid)
        units    = fetch_units(sid)
        apps     = fetch_station_apps(sid) if sid else \
                   supabase_client.table("applications").select(
                       "application_id,retailer_id,station_id,unit_id,status,"
                       "ai_match_score,ai_success_score,est_revenue_thb_mo,"
                       "est_foot_traffic_pct,financial_health_score"
                   ).order("ai_match_score", desc=True).limit(30).execute().data
        app_ids  = [a["application_id"] for a in apps] if apps else []
        ml_out   = fetch_ml_outputs(app_ids)
        return (
            "=== DATABASE CONTEXT ===\n\n"
            + _fmt(stations, "Station Details")
            + _fmt(units,    "Units / Available Spaces")
            + _fmt(apps,     "Applications (sorted by AI match score)")
            + _fmt(ml_out,   "ML Model Outputs")
        )


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

_OUTPUT_FORMAT = """
Always respond in this format:

**Summary (English)**
3–5 sentences. Lead with the key finding. Include specific numbers (THB, %, scores, names).
One risk, one opportunity. No bullet points inside the paragraph.

**สรุป (ภาษาไทย)**
Same 3–5 sentences in natural professional Thai. Same rules.

End with one short follow-up question to continue the conversation.
"""

SYSTEM_RETAILER = textwrap.dedent("""
    You are PTG AI — a conversational business advisor for retailers on the PTG platform in Thailand.
    You help retailers understand their store performance, forecast trends, and find the best station locations.
    Use only the database context provided. Always cite specific numbers.
    Keep answers focused and concise. Be warm and professional.
""") + _OUTPUT_FORMAT

SYSTEM_LANDLORD = textwrap.dedent("""
    You are PTG AI — a conversational property advisor for PTG station landlords in Thailand.
    You help landlords identify the best tenant candidates, review applications, and optimise station revenue.
    Use only the database context provided. Always cite specific numbers.
    Keep answers focused and concise. Be warm and professional.
""") + _OUTPUT_FORMAT


def call_gemini_stream(role, history, question, context):
    """Returns a streaming generator — each chunk is a string token."""
    system = SYSTEM_RETAILER if role == "retailer" else SYSTEM_LANDLORD

    messages = [
        {"role": "user",  "parts": [{"text": system}]},
        {"role": "model", "parts": [{"text": "Understood. I am PTG AI, ready to help."}]},
    ]
    for msg in history:
        messages.append({
            "role":  msg["role"],
            "parts": [{"text": msg["content"]}]
        })
    messages.append({
        "role": "user",
        "parts": [{"text": f"{question}\n\n[Database context:]\n{context}"}]
    })

    for chunk in gemini_client.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=messages,
    ):
        if chunk.text:
            yield chunk.text


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

if "role"             not in st.session_state: st.session_state.role             = None
if "user_id"          not in st.session_state: st.session_state.user_id          = ""
if "history"          not in st.session_state: st.session_state.history          = []
if "started"          not in st.session_state: st.session_state.started          = False
if "pending_question" not in st.session_state: st.session_state.pending_question = None


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">PTG Retailer</div>
        <div class="sidebar-brand-sub">Intelligence Suite</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    pages = [
        ("📊", "Dashboard"),
        ("📈", "Performance"),
        ("🎯", "ML Predictions"),
        ("📤", "Submit Store Data"),
        ("📋", "My Applications"),
        ("✨", "AI Advisor"),
    ]
    for icon, label in pages:
        is_active = label == "AI Advisor"
        cls = "nav-link active" if is_active else "nav-link"
        st.markdown(f'<div class="{cls}">{icon}&nbsp;&nbsp;{label}</div>', unsafe_allow_html=True)

    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)

    # User info at bottom
    if st.session_state.started and st.session_state.user_id:
        uid = st.session_state.user_id
        initials = uid[:2].upper()
        role_label = "Retailer" if st.session_state.role == "retailer" else "Landlord"
        st.markdown(f"""
        <div class="sidebar-user">
            <div class="sidebar-avatar">{initials}</div>
            <div>
                <div class="sidebar-user-name">{uid}</div>
                <div class="sidebar-user-role">{role_label} Account</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    
    if st.session_state.started:
        if st.button("🚪 Switch Account", use_container_width=True):
            st.session_state.role    = None
            st.session_state.user_id = ""
            st.session_state.history = []
            st.session_state.started = False
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

col_main, col_pad = st.columns([1, 0.02])

with col_main:
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # ── ONBOARDING — pick role + ID ──────────────────────────────────────────
    if not st.session_state.started:
        st.markdown('<div class="page-title">AI Advisor</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#FFFFFF; border-radius:32px; padding:40px;
                    box-shadow:0 1px 2px rgba(0,0,0,0.05); max-width:560px; margin-bottom:32px;">
            <div style="font-family:'Newsreader',serif; font-size:24px; color:#1A1C18; margin-bottom:8px;">
                Who are you today?
            </div>
            <div style="font-size:14px; color:#78716C; margin-bottom:24px;">
                Select your role and enter your ID to start your AI-powered session.
            </div>
        </div>
        """, unsafe_allow_html=True)

        role_choice = st.radio(
            "Role",
            ["🛍️  Retailer", "🏢  Landlord"],
            horizontal=True,
            label_visibility="collapsed"
        )
        role = "retailer" if "Retailer" in role_choice else "landlord"

        placeholder = "e.g. RET-001" if role == "retailer" else "e.g. STN-001"
        user_id = st.text_input(
            "Your ID",
            placeholder=placeholder,
            label_visibility="collapsed"
        )

        example_ids = (
            "Try: RET-001 · RET-002 · RET-003"
            if role == "retailer"
            else "Try: STN-001 · STN-002 · STN-003"
        )
        st.caption(example_ids)

        if st.button("✨  Start Session", use_container_width=False):
            if user_id.strip():
                st.session_state.role    = role
                st.session_state.user_id = user_id.strip().upper()
                st.session_state.history = []
                st.session_state.started = True
                st.rerun()
            else:
                st.warning("Please enter your ID first.")

    # ── MAIN ADVISOR PAGE ────────────────────────────────────────────────────
    else:
        role    = st.session_state.role
        user_id = st.session_state.user_id
        title   = "AI Retailer Advisor" if role == "retailer" else "AI Landlord Advisor"

        st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)

        # ── Bento hero cards ─────────────────────────────────────────────────
        st.markdown("""
        <div class="bento-row">
            <div class="hero-card-left">
                <div class="live-badge">
                    <div class="live-dot"></div>
                    <div class="live-text">Live Intelligence Report</div>
                </div>
                <div class="hero-headline">
                    Ask anything about your business performance, station matches, or growth opportunities.
                </div>
                <div class="hero-stats">
                    <div>
                        <div class="hero-stat-label">Location Score</div>
                        <div class="hero-stat-value">92 <span style="font-size:16px;color:#A8A29E">/100</span></div>
                    </div>
                    <div>
                        <div class="hero-stat-label">Revenue Growth</div>
                        <div class="hero-stat-value green">+18%</div>
                    </div>
                </div>
            </div>
            <div class="hero-card-right">
                <div class="forecast-label">Expansion Forecast</div>
                <div class="forecast-title">Projected Q4 Shift in Consumer Behavior</div>
                <div class="forecast-body">
                    ML models indicate a 14% shift in weekday traffic patterns towards premium items.
                    Early adoption could secure market dominance.
                </div>
                <button class="forecast-btn">View Strategic Forecast →</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Strategic recommendation cards ───────────────────────────────────
        st.markdown('<div class="rec-section-title">Strategic Recommendations</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="rec-grid">
            <div class="rec-card">
                <div class="rec-icon-wrap">📅</div>
                <div class="rec-card-title">Optimize Saturday Demand</div>
                <div class="rec-card-body">Redistribute staffing to handle the 22% surge in afternoon traffic identified in Rama 9 outlets.</div>
                <div class="rec-tag green">HIGH PRIORITY !</div>
            </div>
            <div class="rec-card">
                <div class="rec-icon-wrap">📦</div>
                <div class="rec-card-title">Dynamic Bundling Opportunity</div>
                <div class="rec-card-body">Test coffee + bakery bundles during the 08:00–09:30 window to capture expanding commuter volume.</div>
                <div class="rec-tag grey">MEDIUM IMPACT</div>
            </div>
            <div class="rec-card">
                <div class="rec-icon-wrap">🏪</div>
                <div class="rec-card-title">Real Estate Expansion</div>
                <div class="rec-card-body">Three optimal vacant units identified within a 500m radius of your current top-performing cluster.</div>
                <div class="rec-tag dark">NEW INSIGHT</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Chat section ──────────────────────────────────────────────────────
        st.markdown('<div class="chat-section">', unsafe_allow_html=True)

        # Empty state
        if not st.session_state.history:
            st.markdown("""
            <div style="text-align:center; padding:32px 0; color:#A8A29E;">
                <div style="font-size:32px; margin-bottom:8px;">✨</div>
                <div style="font-family:'Newsreader',serif; font-size:18px; color:#78716C;">
                    Your AI advisor is ready
                </div>
                <div style="font-size:13px; margin-top:4px;">Ask anything about your business below</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Render existing history with st.chat_message ──────────────────────
        # st.chat_message handles layout correctly — no duplication
        for msg in st.session_state.history:
            avatar = user_id[:2].upper() if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        # ── Suggestion chips ──────────────────────────────────────────────────
        if role == "retailer":
            chips = [
                "How is my store performing?",
                "What is my Q3 footfall forecast?",
                "Which station best matches my business?",
            ]
        else:
            chips = [
                "Who are my top 3 tenant candidates?",
                "Compare yield with last quarter",
                "Forecast for 2025 expansion",
            ]

        chip_cols = st.columns(len(chips))
        for i, chip in enumerate(chips):
            with chip_cols[i]:
                if st.button(chip, key=f"chip_{i}", use_container_width=True):
                    st.session_state.pending_question = chip
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)  # end chat-section

        # ── Chat input (fixed at bottom of page) ─────────────────────────────
        chat_question = st.chat_input(
            "Ask about regional trends, performance, station matches...",
        )

        # Pick from chat_input OR chip button (chip sets pending_question then reruns)
        question = chat_question or st.session_state.pop("pending_question", None)

        # ── Handle question — render once, stream once, save once ─────────────
        if question:
            question = question.strip()

            # 1. Show user message
            with st.chat_message("user", avatar=user_id[:2].upper()):
                st.markdown(question)
            st.session_state.history.append({"role": "user", "content": question})

            # 2. Stream AI response
            with st.chat_message("assistant", avatar="🤖"):
                try:
                    ctx = build_context(role, user_id, question)
                    full_answer = st.write_stream(
                        call_gemini_stream(
                            role,
                            st.session_state.history[:-1],
                            question,
                            ctx,
                        )
                    )
                except Exception as e:
                    full_answer = f"⚠️ Error: {str(e)[:200]}"
                    st.error(full_answer)

            # 3. Save to history — no rerun needed, already rendered above
            st.session_state.history.append({"role": "model", "content": full_answer})

    st.markdown('</div>', unsafe_allow_html=True)  # end main-content
