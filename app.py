import streamlit as st
from google import genai

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="PTG Retail Platform - AI Advisor", layout="wide")
st.title('⛽ PTG Retail Platform: AI Landlord & Retail Advisor')

# 2. Initialize Client จาก st.secrets
try:
    gemini_api_key = st.secrets["gemini_api_key"]
    gmn_client = genai.Client(api_key=gemini_api_key)
except KeyError:
    st.error("กรุณาตั้งค่า gemini_api_key ใน st.secrets หรือ .streamlit/secrets.toml ก่อนใช้งาน")
    st.stop()

# 3. Sidebar สำหรับเลือก Mode ของ AI
st.sidebar.header("⚙️ การตั้งค่า AI Persona")
mode_selection = st.sidebar.radio(
    "เลือกมุมมองการวิเคราะห์:",
    ("landlord (มุมมองเจ้าของพื้นที่)", "retail (มุมมองผู้บริโภค)")
)
current_mode = "landlord" if "landlord" in mode_selection else "retail"

# 4. ฟังก์ชันประมวลผล
def generate_gemini_answer(prompt, mode="landlord"):
    PERSONA_PROMPTS = {
        "landlord": (
            "คุณคือ Leasing Strategy Manager และ Asset Optimizer สำหรับธุรกิจ Retail ในสถานีบริการน้ำมัน "
            "หน้าที่ของคุณคือวิเคราะห์ข้อมูลเพื่อแนะนำ 'ผู้เช่าประเภทใด' ที่จะสร้าง Rental Yield และ Synergy สูงสุด "
            "ภารกิจ: วิเคราะห์ Optimal Tenant Mix เน้นรายได้ระยะยาวและการใช้พื้นที่คุ้มค่า (Yield per Sq.m.)\n\n"
            "รูปแบบการตอบกลับ: 1. Top 3 Recommended Tenant Types, 2. Landlord Value Proposition, "
            "3. Site Compatibility Analysis, 4. Risk & Opportunity Score"
        ),
        "retail": (
            "คุณคือผู้เชี่ยวชาญด้าน Business Intelligence และ Retail Strategy ที่เชี่ยวชาญการวิเคราะห์ทำเลสถานี PTG "
            "เพื่อจับคู่ความต้องการของผู้บริโภคกับประเภทร้านค้าที่เหมาะสม (Matching Engine)\n\n"
            "ภารกิจ: สร้าง Recommended Retail Concepts โดยเรียงลำดับตามความเหมาะสม พร้อมเหตุผลและตัวเลขคาดการณ์\n\n"
            "รูปแบบการตอบกลับ: 1. Top 3 Recommended Concepts, 2. Strategic Rationale, "
            "3. Predicted Metrics (Demand Score, Target Group, Potential Revenue)"
        )
    }

    try:
        system_context = PERSONA_PROMPTS.get(mode, PERSONA_PROMPTS["landlord"])
        
        # ใช้ gemini-2.5-flash ตัวเต็มเพื่อคุณภาพการวิเคราะห์ Data ที่ดีกว่า lite
        response = gmn_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Station Data Input:\n{prompt}",
            config=genai.types.GenerateContentConfig(
                system_instruction=system_context,
                temperature=0.3, # ลด Temp เพื่อให้ตอบอิงตามข้อมูลจริง ไม่คิดไปเอง
            )
        )
        return response.text

    except Exception as e:
        return f"Error during Gemini text generation: {e}"

# 5. ระบบ Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    # เพิ่มข้อความต้อนรับ
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "สวัสดีครับ ผมคือ AI Advisor สำหรับ PTG Platform กรุณาวางข้อมูล Station Data (เช่น ปริมาณรถ, ข้อมูลลูกค้า, ขนาดพื้นที่) ลงในช่องแชทเพื่อเริ่มการวิเคราะห์ครับ"
    })

# แสดงประวัติการแชททั้งหมด
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. รับ Input จากผู้ใช้
if prompt := st.chat_input("วางข้อมูล Station Data ที่นี่..."):
    # แสดงข้อความผู้ใช้
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ประมวลผลและแสดงผลจาก AI
    with st.chat_message("assistant"):
        with st.spinner(f"กำลังวิเคราะห์ข้อมูลในมุมมอง {current_mode}..."):
            response = generate_gemini_answer(prompt, mode=current_mode)
            st.markdown(response)
            
    # บันทึกคำตอบ AI ลง History
    st.session_state.messages.append({"role": "assistant", "content": response})
