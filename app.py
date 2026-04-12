import streamlit as st
from google import genai

# 1. Page Configuration
st.set_page_config(page_title="PTG Retail Platform", layout="wide")

# 2. Custom CSS (Premium Design based on Reference)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

    .stApp { background-color: #f9f9f9; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e5e7eb; }
    
    /* Typography */
    .serif-title { font-family: 'Playfair Display', serif; color: #111827; font-size: 3.5rem; margin-bottom: 30px; }
    .card-title { font-family: 'Playfair Display', serif; font-size: 2.2rem; line-height: 1.2; }
    
    /* Highlight Tags */
    .live-tag { color: #4c6a23; font-weight: bold; background: #f0fdf4; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; letter-spacing: 0.5px; }
    
    /* Main Cards */
    .white-card { background: white; padding: 40px; border-radius: 28px; border: 1px solid #f3f4f6; box-shadow: 0 10px 30px rgba(0,0,0,0.02); height: 100%; }
    .green-card { background: #4c6a23; color: white; padding: 40px; border-radius: 28px; height: 100%; box-shadow: 0 15px 35px rgba(76, 106, 35, 0.2); }
    .landlord-green-card { background: #96c93e; color: #111827; padding: 40px; border-radius: 28px; height: 100%; }

    /* Strategic Recommendation Cards */
    .rec-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #f3f4f6; min-height: 220px; margin-bottom: 20px; }
    .icon-box { background: #f9f9f9; width: 45px; height: 45px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; font-size: 1.2rem; }

    /* Buttons */
    .custom-btn { background: #96c93e; color: #4c6a23; border: none; padding: 12px 25px; border-radius: 30px; font-weight: bold; width: 100%; margin-top: 20px; cursor: pointer; }
    .dark-btn { background: #111827; color: white; border: none; padding: 12px 25px; border-radius: 30px; font-weight: bold; width: 100%; margin-top: 20px; cursor: pointer; }

    /* Chat Area */
    .chat-section { background: #ffffff; padding: 30px; border-radius: 35px; margin-top: 40px; border: 1px solid #f3f4f6; }
    
    /* Metrics */
    .metric-label { color: #6b7280; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 5px; font-weight: 600; }
    .metric-value { font-size: 2.2rem; font-weight: bold; color: #111827; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Dummy Data (10 Stations & 5 Business Types) ---

BUSINESS_TYPES = {
    "Artisan Café / Coffee": "เน้นพรีเมียม, Co-working space, เหมาะกับกลุ่มคนทำงานและนักเดินทางที่พักนาน",
    "Health & Wellness / Pharmacy": "ยาสามัญและอาหารเสริม, เหมาะกับชุมชนรอบข้างหรือจุดพักรถทางไกล",
    "Convenience / Mini-mart": "สินค้าอุปโภคบริโภคพื้นฐาน, เน้นความรวดเร็วแบบ Grab-and-Go",
    "Quick-Service Food": "อาหารจานด่วนที่ปรุงง่ายไว เช่น เบอร์เกอร์ หรือข้าวกล่องพรีเมียม",
    "Boutique Apparel / Fashion": "เสื้อผ้าแฟชั่นหรืออุปกรณ์เดินทาง, เหมาะกับแหล่งท่องเที่ยว"
}

STATION_DATABASE = {
    "phuket": {"name": "PTG Phuket Coastal", "traffic": "8,500 v/day", "max_card": "High Spending", "gap": "Artisan Café", "yield": "+15%"},
    "chiang mai": {"name": "PTG Chiang Mai Uni", "traffic": "11,000 v/day", "max_card": "Student/Frequent", "gap": "Quick-Service Food", "yield": "+12%"},
    "saraburi": {"name": "PTG Saraburi Highway", "traffic": "25,000 v/day", "max_card": "Truckers/Families", "gap": "Pharmacy", "yield": "+25%"},
    "bangkok": {"name": "PTG Sukhumvit Prime", "traffic": "15,000 v/day", "max_card": "Office Workers", "gap": "Boutique Apparel", "yield": "+18%"},
    "khon kaen": {"name": "PTG Khon Kaen Center", "traffic": "9,000 v/day", "max_card": "Local Loyalists", "gap": "Convenience", "yield": "+10%"},
    "chonburi": {"name": "PTG Chonburi Industrial", "traffic": "18,000 v/day", "max_card": "Workforce", "gap": "Quick-Service Food", "yield": "+20%"},
    "hat yai": {"name": "PTG Hat Yai Gateway", "traffic": "13,000 v/day", "max_card": "Travelers", "gap": "Health & Wellness", "yield": "+14%"},
    "korat": {"name": "PTG Korat Bypass", "traffic": "22,000 v/day", "max_card": "Long-haulers", "gap": "Quick-Service Food", "yield": "+22%"},
    "ayutthaya": {"name": "PTG Ayutthaya", "traffic": "7,000 v/day", "max_card": "Weekend Tourists", "gap": "Artisan Café", "yield": "+9%"},
    "kanchanaburi": {"name": "PTG Kanchanaburi", "traffic": "6,500 v/day", "max_card": "Nature Lovers", "gap": "Boutique Apparel", "yield": "+11%"}
}

# --- 4. AI Engine Configuration ---

try:
    gemini_api_key = st.secrets["gemini_api_key"]
    gmn_client = genai.Client(api_key=gemini_api_key)
except KeyError:
    st.error("Error: Please set 'gemini_api_key' in your secrets.toml.")
    st.stop()

def get_answer(user_input, mode):
    found_station = next((v for k, v in STATION_DATABASE.items() if k in user_input.lower()), "General PTG Network")
    business_context = "\n".join([f"- {k}: {v}" for k, v in BUSINESS_TYPES.items()])
    
    if mode == "landlord":
        system_instruction = (
            "คุณคือ Leasing Strategy Manager ของ PTG. ตอบให้ตรงประเด็นตาม Data ที่ให้เท่านั้น. "
            "ภารกิจคือวิเคราะห์ Optimal Tenant Mix เพื่อสร้าง Yield per Sq.m. สูงสุด.\n"
            "รูปแบบการตอบ:\n1. Top 3 Recommended Tenant Types\n2. Landlord Value Proposition\n3. Site Compatibility Analysis\n4. Risk & Opportunity Score"
        )
    else:
        system_instruction = (
            "คุณคือ Business Intelligence Expert ของ PTG. ตอบให้ตรงประเด็นตาม Data ที่ให้เท่านั้น. "
            "ภารกิจคือเป็น Matching Engine แนะนำร้านค้าที่เหมาะกับ Demand เพื่อลดความเสี่ยงการลงทุน.\n"
            "รูปแบบการตอบ:\n1. Top 3 Recommended Concepts\n2. Strategic Rationale\n3. Predicted Metrics (Demand Score, Target Group, Daily Revenue)"
        )

    try:
        response = gmn_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Data: {found_station}\nBusinesses: {business_context}\nQuestion: {user_input}",
            config=genai.types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.2)
        )
        return response.text
    except Exception as e:
        return f"AI Error: {e}"

# --- 5. Navigation & Sidebar ---

with st.sidebar:
    st.markdown("<h2 style='color: #111827; font-family: serif;'>PTG Advisor</h2>", unsafe_allow_html=True)
    page = st.radio("Navigation", ["Retailer Advisor", "Landlord Advisor"])
    st.markdown("---")
    st.caption("Advanced ML Core v2.5")
    current_mode = "landlord" if page == "Landlord Advisor" else "retail"

# --- 6. Main Content Layout ---

if page == "Retailer Advisor":
    st.markdown('<h1 class="serif-title">AI Retailer Advisor</h1>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"""
        <div class="white-card">
            <span class="live-tag">● LIVE INTELLIGENCE REPORT</span><br><br>
            <div class="card-title">Identify the best <i style="color: #4c6a23;">Market Gap</i> for your retail investment.</div>
            <br><br>
            <div style="display: flex; gap: 60px;">
                <div><div class="metric-label">Network Traffic</div><div class="metric-value">145K <span style="font-size: 1rem; color: #9ca3af;">v/day</span></div></div>
                <div><div class="metric-label">Market Opportunity</div><div class="metric-value" style="color: #4c6a23;">High 📈</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="green-card">
            <h3 style="color: #96c93e; margin-top:0;">Q4 Retail Forecast</h3>
            <p style="font-size: 1.1rem; opacity: 0.9;">ML models indicate a 14% shift in weekday traffic patterns towards premium services.</p>
            <button class="custom-btn">View Full Report →</button>
        </div>
        """, unsafe_allow_html=True)

else: # Landlord Advisor
    st.markdown('<h1 class="serif-title">AI Landlord Advisor</h1>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"""
        <div class="white-card">
            <span class="live-tag">● PORTFOLIO MONITOR</span><br><br>
            <div class="card-title">Maximize your <i style="color: #96c93e;">Rental Yield</i> per square meter with AI.</div>
            <br><br>
            <div style="display: flex; gap: 60px;">
                <div><div class="metric-label">Occupancy Rate</div><div class="metric-value">91.2%</div></div>
                <div><div class="metric-label">Yield Efficiency</div><div class="metric-value" style="color: #4c6a23;">+22%</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="landlord-green-card">
            <div class="icon-box" style="background: #111827; color: white;">⚡</div>
            <div class="metric-label" style="color: #111827;">ASSET OPTIMIZATION</div>
            <h3 style="margin-top: 10px;">Expansion Forecast</h3>
            <p style="font-size: 1rem; opacity: 0.8;">Rama 9 & Sukhumvit nodes show 35% higher retail demand for Q3-Q4.</p>
            <button class="dark-btn">Audit Portfolio</button>
        </div>
        """, unsafe_allow_html=True)

# Shared Section: Recommendations & Chat
st.markdown("<br><h3 style='font-family: serif; font-size: 2rem;'>Strategic Insights</h3>", unsafe_allow_html=True)
r1, r2, r3 = st.columns(3)
with r1:
    st.markdown('<div class="rec-card"><div class="icon-box">📍</div><h4>Location Analysis</h4><p style="color: #6b7280;">Phuket & Bangkok nodes are showing top-tier spending patterns.</p><b>Priority: High</b></div>', unsafe_allow_html=True)
with r2:
    st.markdown('<div class="rec-card"><div class="icon-box">☕</div><h4>Tenant Synergy</h4><p style="color: #6b7280;">Coffee shops are driving 18% higher dwell time in highway stations.</p><b>Insight: New</b></div>', unsafe_allow_html=True)
with r3:
    st.markdown('<div class="rec-card"><div class="icon-box">📊</div><h4>Traffic Predict</h4><p style="color: #6b7280;">Predicted 22% surge in Saraburi traffic due to upcoming holidays.</p><b>ML Status: Active</b></div>', unsafe_allow_html=True)

# --- 7. Chat Interface ---
st.markdown('<div class="chat-section">', unsafe_allow_html=True)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"สวัสดีครับ! ผม AI {page} ประจำแพลตฟอร์ม PTG พร้อมวิเคราะห์ข้อมูลให้คุณแล้วครับ"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("ถามเกี่ยวกับทำเล หรือ แนวโน้มธุรกิจ (เช่น PTG Phuket ควรทำอะไร?)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI is calculating metrics..."):
            response = get_answer(prompt, current_mode)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
st.markdown('</div>', unsafe_allow_html=True)
