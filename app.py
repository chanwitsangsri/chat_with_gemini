import streamlit as st

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PTG AI Advisor",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DUMMY DATA
# ─────────────────────────────────────────────
BUSINESS_TYPES = {
    "Artisan Café / Coffee": "เน้นพรีเมียม, Co-working space, เหมาะกับกลุ่มคนทำงานและนักเดินทางที่พักนาน",
    "Health & Wellness / Pharmacy": "ยาสามัญและอาหารเสริม, เหมาะกับชุมชนรอบข้างหรือจุดพักรถทางไกล",
    "Convenience / Mini-mart": "สินค้าอุปโภคบริโภคพื้นฐาน, เน้นความรวดเร็วแบบ Grab-and-Go",
    "Quick-Service Food": "อาหารจานด่วนที่ปรุงง่ายไว เช่น เบอร์เกอร์ หรือข้าวกล่องพรีเมียม",
    "Boutique Apparel / Fashion": "เสื้อผ้าแฟชั่นหรืออุปกรณ์เดินทาง, เหมาะกับแหล่งท่องเที่ยว",
}

STATION_DATABASE = {
    "phuket":      {"name": "PTG Phuket Coastal",      "traffic": "8,500 v/day",  "max_card": "High Spending",      "gap": "Artisan Café",      "yield": "+15%"},
    "chiang mai":  {"name": "PTG Chiang Mai Uni",       "traffic": "11,000 v/day", "max_card": "Student/Frequent",   "gap": "Quick-Service Food","yield": "+12%"},
    "saraburi":    {"name": "PTG Saraburi Highway",     "traffic": "25,000 v/day", "max_card": "Truckers/Families",  "gap": "Pharmacy",          "yield": "+25%"},
    "bangkok":     {"name": "PTG Sukhumvit Prime",      "traffic": "15,000 v/day", "max_card": "Office Workers",     "gap": "Boutique Apparel",  "yield": "+18%"},
    "khon kaen":   {"name": "PTG Khon Kaen Center",     "traffic": "9,000 v/day",  "max_card": "Local Loyalists",    "gap": "Convenience",       "yield": "+10%"},
    "chonburi":    {"name": "PTG Chonburi Industrial",  "traffic": "18,000 v/day", "max_card": "Workforce",          "gap": "Quick-Service Food","yield": "+20%"},
    "hat yai":     {"name": "PTG Hat Yai Gateway",      "traffic": "13,000 v/day", "max_card": "Travelers",          "gap": "Health & Wellness", "yield": "+14%"},
    "korat":       {"name": "PTG Korat Bypass",         "traffic": "22,000 v/day", "max_card": "Long-haulers",       "gap": "Quick-Service Food","yield": "+22%"},
    "ayutthaya":   {"name": "PTG Ayutthaya",            "traffic": "7,000 v/day",  "max_card": "Weekend Tourists",   "gap": "Artisan Café",      "yield": "+9%"},
    "kanchanaburi":{"name": "PTG Kanchanaburi",         "traffic": "6,500 v/day",  "max_card": "Nature Lovers",      "gap": "Boutique Apparel",  "yield": "+11%"},
}

# Quick recommendation cards per mode
LANDLORD_CARDS = [
    {"icon": "👥", "title": "Optimize Tenant Mix for Lat Phrao 71",
     "desc": "Current EV station dwell time suggests a 15% higher demand for quick-service retail than currently allocated.",
     "tag": "IMPLEMENT NOW", "tag_color": "#3a5a1c"},
    {"icon": "💰", "title": "Revenue Growth Opportunity",
     "desc": "Dynamic pricing models for high-traffic weekend slots could increase secondary revenue streams by ฿4.2k/mo.",
     "tag": "VIEW ANALYSIS", "tag_color": "#3a5a1c"},
    {"icon": "🛡️", "title": "Risk Mitigation",
     "desc": "Localized power grid volatility detected in the Bang Kapi area. Recommend backup battery station expansion.",
     "tag": "EVALUATE RISK", "tag_color": "#8B4513"},
]

RETAILER_CARDS = [
    {"icon": "📅", "title": "Optimize Saturday Demand",
     "desc": "Redistribute staffing levels to handle the 22% surge in afternoon traffic identified in Rama 9 outlets.",
     "tag": "High Priority !", "tag_color": "#3a5a1c"},
    {"icon": "☕", "title": "Dynamic Bundling Opportunity",
     "desc": "Test coffee + bakery bundles during the 08:00 – 09:30 window to capture expanding commuter volume.",
     "tag": "Medium Impact", "tag_color": "#5a5a1c"},
    {"icon": "🏪", "title": "Rama 9 Real Estate Expansion",
     "desc": "Three optimal vacant units identified within a 500m radius of current top-performing cluster.",
     "tag": "New Insight", "tag_color": "#1c4a5a"},
]

# ─────────────────────────────────────────────
# AI ENGINE
# ─────────────────────────────────────────────
def get_answer(user_input: str, mode: str) -> str:
    # ── Get API key ──
    api_key = st.secrets.get("gemini_api_key", "")
    if not api_key:
        return "⚠️ กรุณาตั้งค่า `gemini_api_key` ใน secrets.toml ก่อนใช้งาน"

    found_station = next(
        (v for k, v in STATION_DATABASE.items() if k in user_input.lower()),
        "General PTG Network",
    )
    business_context = "\n".join([f"- {k}: {v}" for k, v in BUSINESS_TYPES.items()])

    if mode == "landlord":
        system_instruction = (
            "คุณคือ Leasing Strategy Manager ของ PTG. ตอบให้ตรงประเด็นตาม Data ที่ให้เท่านั้น. "
            "ภารกิจคือวิเคราะห์ Optimal Tenant Mix เพื่อสร้าง Yield per Sq.m. สูงสุด.\n"
            "รูปแบบการตอบ:\n1. Top 3 Recommended Tenant Types\n2. Landlord Value Proposition\n"
            "3. Site Compatibility Analysis\n4. Risk & Opportunity Score"
        )
    else:
        system_instruction = (
            "คุณคือ Business Intelligence Expert ของ PTG. ตอบให้ตรงประเด็นตาม Data ที่ให้เท่านั้น. "
            "ภารกิจคือเป็น Matching Engine แนะนำร้านค้าที่เหมาะกับ Demand เพื่อลดความเสี่ยงการลงทุน.\n"
            "รูปแบบการตอบ:\n1. Top 3 Recommended Concepts\n2. Strategic Rationale\n"
            "3. Predicted Metrics (Demand Score, Target Group, Daily Revenue)"
        )

    try:
        # ── Try new google-genai SDK first (>= 0.8) ──
        from google import genai as genai_new
        client = genai_new.Client(api_key=api_key)
        full_prompt = (
            f"[System] {system_instruction}\n\n"
            f"Data: {found_station}\nBusinesses: {business_context}\nQuestion: {user_input}"
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
        )
        return response.text
    except Exception:
        pass

    try:
        # ── Fallback: classic google-generativeai SDK ──
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_instruction,
        )
        response = model.generate_content(
            f"Data: {found_station}\nBusinesses: {business_context}\nQuestion: {user_input}",
            generation_config={"temperature": 0.2},
        )
        return response.text
    except Exception as e:
        return f"⚠️ AI Error: {e}"

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root palette (matches screenshots) ── */
:root {
    --green-dark:   #2d4a1a;
    --green-mid:    #3e6b22;
    --green-accent: #5a8c2f;
    --green-light:  #8ab55a;
    --cream:        #f5f4ef;
    --card-bg:      #ffffff;
    --text-primary: #1a1a1a;
    --text-secondary: #374151;
    --text-muted:   #6b7280;
    --border:       #e5e7eb;
    --hero-bg:      #f9f8f4;
}

/* ── Reset Streamlit chrome ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--cream) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-primary) !important;
}

/* Force all text in main area to be readable dark */
[data-testid="stMainBlockContainer"] p,
[data-testid="stMainBlockContainer"] span,
[data-testid="stMainBlockContainer"] div,
[data-testid="stMarkdownContainer"] p {
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1100px; }

/* ── Sidebar brand ── */
.sidebar-brand {
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--text-primary);
    padding: 0 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
}

/* ── Page title ── */
.ptg-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: var(--text-primary);
    margin-bottom: 1.5rem;
    line-height: 1.15;
}

/* ── Hero row ── */
.hero-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }

/* Live Intelligence Card */
.hero-intel {
    flex: 1.4;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
}
.live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.68rem; font-weight: 600; letter-spacing: .08em;
    color: var(--green-mid); text-transform: uppercase;
    background: #edf5e5; border-radius: 20px;
    padding: 4px 10px; margin-bottom: 1rem;
}
.live-dot { width:7px; height:7px; border-radius:50%; background:var(--green-mid); }
.hero-headline {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem; line-height: 1.3;
    color: var(--text-primary); margin-bottom: 1.4rem;
}
.hero-headline em { color: var(--green-accent); font-style: italic; }
.metric-row { display:flex; gap:2.5rem; }
.metric-block label {
    font-size:.68rem; letter-spacing:.08em; text-transform:uppercase;
    color: var(--text-muted); display:block; margin-bottom:2px;
}
.metric-block .metric-val {
    font-size: 2rem; font-weight: 700; color: var(--text-primary);
}
.metric-block .metric-val span { font-size:1rem; color:var(--text-muted); }
.metric-block .metric-val.green { color: var(--green-accent); }

/* Forecast Card */
.hero-forecast {
    flex: 1;
    background: var(--green-dark);
    border-radius: 16px;
    padding: 2rem;
    color: #fff;
    display:flex; flex-direction:column; justify-content:space-between;
}
.forecast-label {
    font-size:.65rem; letter-spacing:.12em; text-transform:uppercase;
    color: rgba(255,255,255,.6); margin-bottom:.5rem;
}
.forecast-icon {
    width:36px;height:36px;border-radius:10px;
    background:rgba(255,255,255,.15);
    display:flex;align-items:center;justify-content:center;
    font-size:1.1rem;margin-bottom:1rem;
}
.hero-forecast h3 {
    font-family:'DM Serif Display',serif;
    font-size:1.5rem;line-height:1.2;margin-bottom:.8rem;
}
.hero-forecast p { font-size:.82rem;color:rgba(255,255,255,.75);line-height:1.6;margin-bottom:1.2rem; }
.btn-forecast {
    display:inline-block;background:var(--green-accent);
    color:#fff;border-radius:30px;padding:10px 20px;
    font-size:.82rem;font-weight:600;text-decoration:none;cursor:pointer;
    border:none;transition:background .2s;
}
.btn-forecast:hover { background:var(--green-light); }

/* ── Section heading ── */
.section-heading {
    font-family:'DM Serif Display',serif;
    font-size:1.4rem;color:var(--text-primary);
    margin: .5rem 0 1rem;
}

/* ── Recommendation cards ── */
.rec-row { display:flex;gap:1rem;margin-bottom:1.5rem; }
.rec-card {
    flex:1;background:var(--card-bg);border:1px solid var(--border);
    border-radius:14px;padding:1.4rem;
    transition:box-shadow .2s,transform .2s;
}
.rec-card:hover { box-shadow:0 6px 24px rgba(0,0,0,.07);transform:translateY(-2px); }
.rec-icon {
    width:38px;height:38px;border-radius:10px;
    background:#f0f4ec;display:flex;align-items:center;
    justify-content:center;font-size:1.1rem;margin-bottom:.9rem;
}
.rec-card h4 { font-size:.95rem;font-weight:600;color:var(--text-primary);margin-bottom:.5rem;line-height:1.35; }
.rec-card p  { font-size:.8rem;color:var(--text-muted);line-height:1.6;margin-bottom:.9rem; }
.rec-tag     { font-size:.7rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase; }

/* ── Chat section ── */
.chat-wrap {
    background:var(--card-bg);border:1px solid var(--border);
    border-radius:16px;padding:1.5rem;
}
.suggestion-row { display:flex;gap:.6rem;flex-wrap:wrap;margin-top:.8rem; }
.suggestion-chip {
    font-size:.75rem;color:var(--text-muted);border:1px solid var(--border);
    border-radius:20px;padding:5px 12px;cursor:pointer;
    background:transparent;transition:background .15s;
}
.suggestion-chip:hover { background:var(--cream); }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius:12px !important;
    background: transparent !important;
}

/* ── Chat bubbles ── */
/* Assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.6rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}
/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #edf5e5 !important;
    border: 1px solid #c8d8b8 !important;
    border-radius: 16px !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.6rem !important;
}
/* Text inside bubbles must be dark */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #1a1a1a !important;
    font-size: 0.9rem !important;
    line-height: 1.65 !important;
}
/* Avatar icons */
[data-testid="stChatMessageAvatarAssistant"] {
    background: var(--green-dark) !important;
    border-radius: 50% !important;
}
[data-testid="stChatMessageAvatarUser"] {
    background: var(--green-accent) !important;
    border-radius: 50% !important;
}

/* ── Kill the dark bottom bar completely ── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
.stBottom, .st-emotion-cache-1gulkj5,
section[data-testid="stBottom"] {
    background: var(--cream) !important;
    background-color: var(--cream) !important;
    border-top: 1px solid var(--border) !important;
    box-shadow: none !important;
}
/* Also target any fixed/sticky footer Streamlit might inject */
footer, [data-testid="InputInstructions"] {
    background: var(--cream) !important;
    color: var(--text-muted) !important;
}
[data-testid="stChatInput"] {
    background: var(--cream) !important;
}
[data-testid="stChatInput"] > div {
    background: var(--cream) !important;
}
[data-testid="stChatInput"] textarea {
    border-radius: 30px !important;
    border: 1.5px solid #c8d8b8 !important;
    padding: 12px 20px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .88rem !important;
    background: #ffffff !important;
    color: var(--text-primary) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--green-accent) !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(90,140,47,0.15) !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #9ca3af !important;
}
[data-testid="stChatInput"] button {
    background: var(--green-dark) !important;
    border-radius: 50% !important;
    color: #fff !important;
}

/* ── Mode toggle buttons ── */
div[data-testid="column"] button {
    border-radius: 30px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: .82rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "mode" not in st.session_state:
    st.session_state.mode = "retailer"
if "messages" not in st.session_state:
    st.session_state.messages = {}

def msgs():
    key = st.session_state.mode
    if key not in st.session_state.messages:
        greeting = (
            "สวัสดีครับ! ผม **AI Landlord Advisor** ประจำแพลตฟอร์ม PTG 🏗️\n\n"
            "พร้อมวิเคราะห์ Tenant Mix · Yield per Sq.m · และโอกาสขยายสาขาให้คุณแล้วครับ"
            if key == "landlord" else
            "สวัสดีครับ! ผม **AI Retailer Advisor** ประจำแพลตฟอร์ม PTG ☕\n\n"
            "พร้อมแนะนำทำเลที่เหมาะสม · วิเคราะห์ Demand · และลดความเสี่ยงการลงทุนให้คุณแล้วครับ"
        )
        st.session_state.messages[key] = [{"role": "assistant", "content": greeting}]
    return st.session_state.messages[key]

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    mode = st.session_state.mode
    brand = "PTG Landlord" if mode == "landlord" else "PTG Retailer"
    st.markdown(f'<div class="sidebar-brand">⛽ {brand}</div>', unsafe_allow_html=True)

    if mode == "landlord":
        nav_items = ["Overview","My Stations","Applications","Tenants","Revenue","**AI Advisor**"]
    else:
        nav_items = ["Dashboard","Performance","ML Predictions","Submit Store Data","My Applications","**AI Advisor**"]

    for item in nav_items:
        is_active = "**" in item
        label = item.replace("**","")
        if is_active:
            st.markdown(f"""
            <div style="padding:8px 12px;border-radius:8px;background:#edf5e5;
                        border-left:3px solid #5a8c2f;font-weight:600;
                        color:#3e6b22;font-size:.88rem;margin-bottom:4px;">
                ✦ {label}
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="padding:8px 12px;border-radius:8px;color:#6b7280;
                        font-size:.88rem;margin-bottom:4px;cursor:pointer;">
                {label}
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='margin:1.5rem 0;border-color:#e5e7eb;'>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:.75rem;color:#9ca3af;padding:0 .5rem;">Switch mode</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏢 Landlord", use_container_width=True,
                     type="primary" if mode=="landlord" else "secondary"):
            st.session_state.mode = "landlord"
            st.rerun()
    with col2:
        if st.button("🛍 Retailer", use_container_width=True,
                     type="primary" if mode=="retailer" else "secondary"):
            st.session_state.mode = "retailer"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:.75rem;color:#9ca3af;padding:0 .5rem;">🔒 Logout</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
mode = st.session_state.mode
is_landlord = (mode == "landlord")

title = "AI Landlord Advisor" if is_landlord else "AI Retailer Advisor"
st.markdown(f'<div class="ptg-title">{title}</div>', unsafe_allow_html=True)

# ── Hero row ────────────────────────────────
if is_landlord:
    hero_italic = "14% above market"
    hero_rest   = " in the Lat Phrao district."
    metric1_label, metric1_val, metric1_suffix = "OCCUPANCY EFFICIENCY", "89.4", "%"
    metric2_label, metric2_val, metric2_suffix = "RETAIL YIELD YOY", "+22", "%"
    forecast_label  = "EXPANSION FORECAST"
    forecast_icon   = "📈"
    forecast_title  = "Projected Growth for Sukhumvit 62"
    forecast_body   = ("Based on local traffic patterns and the upcoming rail extension, "
                       "this node shows a 35% increase in retail demand by Q4.")
    forecast_btn    = "View Detailed Forecast"
    cards = LANDLORD_CARDS
    suggestions = ['"Compare yield with Nonthaburi"', '"Best performing retail tenant"', '"Forecast for 2025 expansion"']
else:
    hero_italic = "Coffee Corner"
    hero_rest   = " segment is performing 18% above rolling average."
    metric1_label, metric1_val, metric1_suffix = "LOCATION SCORE", "92", " / 100"
    metric2_label, metric2_val, metric2_suffix = "REVENUE GROWTH", "+18", "%"
    forecast_label  = "Q4 CONSUMER SHIFT"
    forecast_icon   = "🔮"
    forecast_title  = "Projected Q4 Shift in Consumer Behavior"
    forecast_body   = ("ML models indicate a 14% shift in weekday traffic patterns towards "
                       "premium breakfast items. Early adoption could secure market dominance in Rama 9.")
    forecast_btn    = "View Strategic Forecast"
    cards = RETAILER_CARDS
    suggestions = ['"Analyze competitors in Sukhumvit"', '"What is my Q3 footfall forecast?"', '"Identify saturation in Rama 9"']

st.markdown(f"""
<div class="hero-row">
  <div class="hero-intel">
    <div class="live-badge"><span class="live-dot"></span>LIVE INTELLIGENCE REPORT</div>
    <div class="hero-headline">Your <em>{hero_italic}</em>{hero_rest}</div>
    <div class="metric-row">
      <div class="metric-block">
        <label>{metric1_label}</label>
        <div class="metric-val">{metric1_val}<span>{metric1_suffix}</span></div>
      </div>
      <div class="metric-block">
        <label>{metric2_label}</label>
        <div class="metric-val green">{metric2_val}<span>{metric2_suffix} ↗</span></div>
      </div>
    </div>
  </div>
  <div class="hero-forecast">
    <div>
      <div class="forecast-label">{forecast_label}</div>
      <div class="forecast-icon">{forecast_icon}</div>
      <h3>{forecast_title}</h3>
      <p>{forecast_body}</p>
    </div>
    <button class="btn-forecast">{forecast_btn} →</button>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Recommendation cards ─────────────────────
st.markdown('<div class="section-heading">Strategic Recommendations</div>', unsafe_allow_html=True)
st.markdown('<div class="rec-row">', unsafe_allow_html=True)
for card in cards:
    st.markdown(f"""
    <div class="rec-card">
      <div class="rec-icon">{card['icon']}</div>
      <h4>{card['title']}</h4>
      <p>{card['desc']}</p>
      <span class="rec-tag" style="color:{card['tag_color']};">{card['tag']} ›</span>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Chat section ─────────────────────────────
st.markdown('<div class="section-heading" style="margin-top:1.5rem;">Ask AI Advisor</div>', unsafe_allow_html=True)

# Suggestion chips
chip_html = "".join(
    f'<span class="suggestion-chip">{s}</span>' for s in suggestions
)
st.markdown(f'<div class="suggestion-row" style="margin-bottom:1rem;">{chip_html}</div>', unsafe_allow_html=True)

for msg in msgs():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ───────────────────────────────
placeholder = "Ask about regional trends, tenant mix, or site performance..."
if prompt := st.chat_input(placeholder):
    msgs().append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI is calculating metrics..."):
            reply = get_answer(prompt, mode)
            st.markdown(reply)
            msgs().append({"role": "assistant", "content": reply})
