

import streamlit as st
from google import genai

# 1. ตั้งค่าหน้าเว็บและธีมสี PTG
st.set_page_config(page_title="PTG Retail Platform", layout="wide")

# Custom CSS สำหรับปรับแต่งสีให้เป็น PTG (เขียว-เหลือง)
st.markdown("""
    <style>
    /* ส่วนหัวและพื้นหลัง Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
        border-right: 3px solid #00A859;
    }
    /* ปรับแต่งสีปุ่ม Streamlit */
    div.stButton > button:first-child {
        background-color: #00A859;
        color: white;
        border-radius: 5px;
    }
    /* สี Header */
    h1 {
        color: #00A859;
        border-bottom: 2px solid #FFD100;
        padding-bottom: 10px;
    }
    /* Chat Input Focus */
    .stChatInput:focus-within {
        border-color: #00A859 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title('⛽ PTG Retail Platform: AI Landlord & Retail Advisor')

# --- 2. Database จำลอง (10 สถานี & 5 ธุรกิจ) ---

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

# --- 3. AI Engine ---

try:
    gemini_api_key = st.secrets["gemini_api_key"]
    gmn_client = genai.Client(api_key=gemini_api_key)
except KeyError:
    st.error("กรุณาตั้งค่า API Key ใน secrets.toml")
    st.stop()

st.sidebar.header("⚙️ AI Persona Settings")
mode_selection = st.sidebar.radio("เลือกมุมมองการวิเคราะห์:", ("Landlord View", "Retailer View"))
current_mode = "landlord" if "Landlord" in mode_selection else "retail"

def get_answer(user_input, mode):
    # ค้นหาข้อมูลสถานีจากคำถาม
    found_station = next((v for k, v in STATION_DATABASE.items() if k in user_input.lower()), "General PTG Context")
    
    # ดึงรายละเอียดธุรกิจเพื่อเป็นแนวทางให้ AI
    business_context = "\n".join([f"- {k}: {v}" for k, v in BUSINESS_TYPES.items()])
    
    prompt_context = f"Station Data Input: {found_station}\n\nValid Business Categories: \n{business_context}"

    # แยก Persona ตาม Requirement ที่คุณกำหนด
    if mode == "landlord":
        system_instruction = (
            "คุณคือ Leasing Strategy Manager และ Asset Optimizer ของ PTG. "
            "ภารกิจ: วิเคราะห์ Optimal Tenant Mix เพื่อสร้าง Rental Yield และ Synergy สูงสุด (Yield per Sq.m.).\n"
            "กฎการตอบ: ให้ตอบตามรูปแบบดังนี้เท่านั้น:\n"
            "1. Top 3 Recommended Tenant Types: (เลือกจาก Business Categories ที่กำหนดให้)\n"
            "2. Landlord Value Proposition: (อธิบายความคุ้มค่า เช่น ดึง Traffic ช่วง Off-peak หรือสัญญาเช่าระยะยาว)\n"
            "3. Site Compatibility Analysis: (วิเคราะห์ความเหมาะสมของพื้นที่และสาธารณูปโภค)\n"
            "4. Risk & Opportunity Score: (ระบุ Yield Potential, Traffic Synergy, และ Churn Risk เป็น High/Medium/Low)"
        )
    else:
        system_instruction = (
            "คุณคือ Business Intelligence และ Retail Strategy Expert ของ PTG. "
            "ภารกิจ: เป็น Matching Engine จับคู่ Demand ของผู้บริโภคกับร้านค้าที่เหมาะสมเพื่อลดความเสี่ยงการเปิดร้านผิดประเภท.\n"
            "กฎการตอบ: ให้ตอบตามรูปแบบดังนี้เท่านั้น:\n"
            "1. Top 3 Recommended Concepts: (เรียงตามความเหมาะสมจากข้อมูล Pattern การใช้จ่าย)\n"
            "2. Strategic Rationale: (เหตุผลเชิงกลยุทธ์ เช่น Morning Traffic สูงเหมาะกับอาหารเช้า)\n"
            "3. Predicted Metrics (Estimate):\n"
            "   - Demand Score: (1-10)\n"
            "   - Target Group: (ระบุกลุ่มเป้าหมายหลัก)\n"
            "   - Potential Daily Revenue: (ประมาณการรายได้ต่อวันเป็นช่วงตัวเลข)"
        )

    try:
        response = gmn_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{prompt_context}\n\nUser Question: {user_input}",
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction, 
                temperature=0.3 # ใช้ Temp ต่ำเพื่อให้ AI ยึดตาม Data และไม่คิดเอง (ตามคำสั่งใน Saved Info)
            )
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- 4. UI Chat Interface ---

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "สวัสดีครับ! ผม AI Advisor ประจำแพลตฟอร์ม PTG วันนี้ต้องการข้อมูลวิเคราะห์พื้นที่หรือหาทำเลเปิดร้านดีครับ?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_query := st.chat_input("ตัวอย่าง: ขายกาแฟปั๊มไหนดี? หรือ PTG Phuket ควรขายอะไร?"):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("กำลังวิเคราะห์ข้อมูลด้วย AI..."):
            answer = get_answer(user_query, current_mode)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
