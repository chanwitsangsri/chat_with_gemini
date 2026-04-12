import streamlit as st
from google import genai

# 1. Page Configuration & Theme Styling
st.set_page_config(page_title="PTG Retail Platform", layout="wide")

# Custom CSS เพื่อปรับแต่ง UI ให้ตรงตามภาพ Reference
st.markdown("""
    <style>
    /* พื้นหลังหลัก (Light Gray) */
    .stApp {
        background-color: #f9f9f9;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* หัวข้อหลักแบบ Serif พรีเมียม */
    .main-title {
        font-family: 'serif';
        color: #111827;
        font-size: 3rem;
        margin-bottom: 10px;
    }

    /* สไตล์การ์ดสีเขียวเข้ม (Projected Q4 Shift) */
    .green-card {
        background-color: #4c6a23;
        color: #ffffff;
        padding: 30px;
        border-radius: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    /* ปุ่มภายในการ์ดสีเขียว */
    .green-card button {
        background-color: #96c93e;
        border: none;
        padding: 10px 20px;
        border-radius: 30px;
        color: #4c6a23;
        font-weight: bold;
        width: 100%;
        cursor: pointer;
    }

    /* กล่องแชทแบบการ์ดขาวพร้อม Soft Shadow */
    [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #f3f4f6 !important;
    }

    /* ปรับปรุง Input แชทให้โค้งมน */
    .stChatInputContainer {
        padding: 10px !important;
        background-color: #ffffff !important;
        border-radius: 50px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* สีของ Radio Selection และปุ่มหลัก */
    .st-bd, [data-testid="stChatInput"] button {
        background-color: #4c6a23 !important;
        color: white !important;
    }
    
    .st-bd { color: #4c6a23 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Dummy Data (10 Stations & 5 Business Types) ---

BUSINESS_TYPES = {
    "Artisan Café / Coffee": "เน้นพรีเมียม, Co-working space, เหมาะกับกลุ่มคนทำงานและนักเดินทางที่จอดพักนาน",
    "Health & Wellness / Pharmacy": "ยาสามัญและอาหารเสริม, เหมาะกับชุมชนรอบข้างหรือจุดพักรถทางไกล",
    "Convenience / Mini-mart": "สินค้าอุปโภคบริโภคพื้นฐาน, เน้นความรวดเร็วแบบ Grab-and-Go",
    "Quick-Service Food": "อาหารจานด่วนที่ปรุงง่ายไว เช่น เบอร์เกอร์ หรือข้าวกล่องพรีเมียม",
    "Boutique Apparel / Fashion": "เสื้อผ้าแฟชั่นหรืออุปกรณ์เดินทาง, เหมาะกับแหล่งท่องเที่ยว"
}

STATION_DATABASE = {
    "phuket": {"name": "PTG Phuket Coastal", "traffic": "8,500 v/day", "max_card": "High Spending", "gap": "Artisan Café"},
    "chiang mai": {"name": "PTG Chiang Mai Uni", "traffic": "11,000 v/day", "max_card": "Student/Frequent", "gap": "Quick-Service Food"},
    "saraburi": {"name": "PTG Saraburi Highway", "traffic": "25,000 v/day", "max_card": "Truckers/Families", "gap": "Pharmacy"},
    "bangkok": {"name": "PTG Sukhumvit Prime", "traffic": "15,000 v/day", "max_card": "Office Workers", "gap": "Boutique Apparel"},
    "khon kaen": {"name": "PTG Khon Kaen Center", "traffic": "9,000 v/day", "max_card": "Local Loyalists", "gap": "Convenience"},
    "chonburi": {"name": "PTG Chonburi Industrial", "traffic": "18,000 v/day", "max_card": "Workforce", "gap": "Quick-Service Food"},
    "hat yai": {"name": "PTG Hat Yai Gateway", "traffic": "13,000 v/day", "max_card": "Travelers", "gap": "Health & Wellness"},
    "korat": {"name": "PTG Korat Bypass", "traffic": "22,000 v/day", "max_card": "Long-haulers", "gap": "Quick-Service Food"},
    "ayutthaya": {"name": "PTG Ayutthaya", "traffic": "7,000 v/day", "max_card": "Weekend Tourists", "gap": "Artisan Café"},
    "kanchanaburi": {"name": "PTG Kanchanaburi", "traffic": "6,500 v/day", "max_card": "Nature Lovers", "gap": "Boutique Apparel"}
}

# --- 3. AI Engine Configuration ---

try:
    gemini_api_key = st.secrets["gemini_api_key"]
    gmn_client = genai.Client(api_key=gemini_api_key)
except KeyError:
    st.error("Error: Please set 'gemini_api_key' in your secrets.toml file.")
    st.stop()

# Sidebar Setup
with st.sidebar:
    st.markdown("<h2 style='color: #4c6a23;'>PTG Platform</h2>", unsafe_allow_html=True)
    mode_selection = st.radio("Select Analysis Persona:", ("Landlord View", "Retailer View"))
    current_mode = "landlord" if "Landlord" in mode_selection else "retail"

def get_answer(user_input, mode):
    # ค้นหาข้อมูลสถานี
    found_station = next((v for k, v in STATION_DATABASE.items() if k in user_input.lower()), "General PTG Network")
    business_context = "\n".join([f"- {k}: {v}" for k, v in BUSINESS_TYPES.items()])
    
    if mode == "landlord":
        system_instruction = (
            "คุณคือ Leasing Strategy Manager ของ PTG. ภารกิจคือวิเคราะห์ Optimal Tenant Mix เพื่อสร้าง Yield per Sq.m. สูงสุด.\n"
            "รูปแบบการตอบ:\n1. Top 3 Recommended Tenant Types\n2. Landlord Value Proposition\n3. Site Compatibility Analysis\n4. Risk & Opportunity Score"
        )
    else:
        system_instruction = (
            "คุณคือ Business Intelligence Expert ของ PTG. ภารกิจคือเป็น Matching Engine แนะนำร้านค้าที่เหมาะกับ Demand.\n"
            "รูปแบบการตอบ:\n1. Top 3 Recommended Concepts\n2. Strategic Rationale\n3. Predicted Metrics (Demand Score, Target Group, Daily Revenue)"
        )

    try:
        response = gmn_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Data: {found_station}\nBusinesses: {business_context}\nQuestion: {user_input}",
            config=genai.types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.3)
        )
        return response.text
    except Exception as e:
        return f"AI Error: {e}"

# --- 4. Main UI Layout ---

st.markdown('<h1 class="main-title">AI Retailer Advisor</h1>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div style="background-color: white; padding: 40px; border-radius: 24px; border: 1px solid #f3f4f6; margin-bottom: 20px;">
        <span style="color: #4c6a23; font-weight: bold; background: #f0fdf4; padding: 5px 15px; border-radius: 20px;">● LIVE SYSTEM ACTIVE</span>
        <h2 style="font-family: serif; font-size: 2.2rem; margin-top: 20px;">Ready to optimize your <i style="color: #4c6a23;">Retail Value</i> with PTG Data.</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="green-card">
        <h3 style="margin-top:0;">Platform Insight</h3>
        <p style="opacity: 0.9; font-size: 0.9rem;">Current mode: <b>{mode_selection}</b>. AI is processing internal fuel and Max Card transaction data for insights.</p>
        <button>Update Forecast</button>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<h3>Strategic Recommendations</h3>", unsafe_allow_html=True)

# --- 5. Chat Interface ---

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "สวัสดีครับ! ผม AI Advisor พร้อมช่วยคุณวิเคราะห์ข้อมูลเชิงลึกของสถานี PTG แล้วครับ"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("ตัวอย่าง: ขายกาแฟปั๊มไหนดี? หรือ PTG Phuket ควรขายอะไร?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing site data..."):
            response = get_answer(prompt, current_mode)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
