import streamlit as st
from roboflow import Roboflow
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
import os

# --- 1. CẤU HÌNH HỆ THỐNG ---
API_KEY_ROBOFLOW = "EkNBEpyZvjbdWCARPUuj" 
PROJECT_ID_1 = "myfirstproject-vbszv"
VERSION_1 = 2 
PROJECT_ID_ROT = "fresh-and-stale-fruits-lrvou"
VERSION_ROT = 1
# API Key Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  
genai.configure(api_key=GEMINI_API_KEY)


data_trai_cay = {
    "apple": {"ten": "Táo", "loi_ich": "🍎 Giàu chất xơ và Vitamin C. Tốt cho tim mạch.", "mon_an": "Salad táo, bánh pie táo.", "calo": "52 kcal/100g"},
    "banana": {"ten": "Chuối", "loi_ich": "🍌 Cung cấp Kali dồi dào, ổn định huyết áp.", "mon_an": "Chè chuối, sinh tố chuối.", "calo": "89 kcal/100g"},
    "beetroot": {"ten": "Củ dền", "loi_ich": "🩸 Giúp hạ huyết áp, cải thiện lưu thông máu.", "mon_an": "Canh củ dền, nước ép.", "calo": "43 kcal/100g"},
    "bell pepper": {"ten": "Ớt chuông", "loi_ich": "🫑 Vitamin C cực cao, giúp sáng mắt.", "mon_an": "Ớt chuông xào bò.", "calo": "20 kcal/100g"},
    "cabbage": {"ten": "Bắp cải", "loi_ich": "🥬 Chứa nhiều Vitamin K tốt cho não bộ.", "mon_an": "Bắp cải cuộn thịt.", "calo": "25 kcal/100g"},
    "capsicum": {"ten": "Ớt chuông (Đà Lạt)", "loi_ich": "🌶️ Giàu chất chống oxy hóa.", "mon_an": "Salad, xào thập cẩm.", "calo": "20 kcal/100g"},
    "carrot": {"ten": "Cà rốt", "loi_ich": "🥕 Nguồn Beta-carotene giúp mắt sáng.", "mon_an": "Nước ép, kho bò.", "calo": "41 kcal/100g"},
    "cauliflower": {"ten": "Súp lơ trắng", "loi_ich": "🥦 Giàu chất xơ ngăn ngừa ung thư.", "mon_an": "Súp lơ xào tỏi.", "calo": "25 kcal/100g"},
    "chilli pepper": {"ten": "Ớt cay", "loi_ich": "🔥 Thúc đẩy trao đổi chất.", "mon_an": "Gia vị, sa tế.", "calo": "40 kcal/100g"},
    "corn": {"ten": "Bắp (Ngô)", "loi_ich": "🌽 Tốt cho tiêu hóa.", "mon_an": "Bắp luộc, súp bắp.", "calo": "86 kcal/100g"},
    "cucumber": {"ten": "Dưa leo", "loi_ich": "🥒 Cấp ẩm và thanh lọc cơ thể.", "mon_an": "Ăn sống, salad.", "calo": "15 kcal/100g"},
    "eggplant": {"ten": "Cà tím", "loi_ich": "🍆 Bảo vệ tế bào não.", "mon_an": "Cà tím nướng mỡ hành.", "calo": "25 kcal/100g"},
    "garlic": {"ten": "Tỏi", "loi_ich": "🧄 Kháng sinh tự nhiên.", "mon_an": "Gia vị xào.", "calo": "149 kcal/100g"},
    "ginger": {"ten": "Gừng", "loi_ich": "🫚 Giữ ấm cơ thể, giảm buồn nôn.", "mon_an": "Trà gừng, gà kho gừng.", "calo": "80 kcal/100g"},
    "grapes": {"ten": "Nho", "loi_ich": "🍇 Chống lão hóa cực mạnh.", "mon_an": "Ăn tươi, nước ép.", "calo": "67 kcal/100g"},
    "jalapeno": {"ten": "Ớt Jalapeno", "loi_ich": "🌶️ Giúp giảm cân.", "mon_an": "Pizza, Tacos.", "calo": "29 kcal/100g"},
    "kiwi": {"ten": "Kiwi", "loi_ich": "🥝 Vitamin C cực cao.", "mon_an": "Sinh tố, bánh kem.", "calo": "61 kcal/100g"},
    "lemon": {"ten": "Chanh vàng", "loi_ich": "🍋 Giải độc gan.", "mon_an": "Nước chanh mật ong.", "calo": "29 kcal/100g"},
    "lettuce": {"ten": "Xà lách", "loi_ich": "🥗 Giúp ngủ ngon.", "mon_an": "Salad trộn.", "calo": "15 kcal/100g"},
    "mango": {"ten": "Xoài", "loi_ich": "🥭 Tốt cho mắt và tiêu hóa.", "mon_an": "Xoài chín, sinh tố.", "calo": "60 kcal/100g"},
    "onion": {"ten": "Hành tây", "loi_ich": "🧅 Kháng viêm tốt.", "mon_an": "Xào thịt bò.", "calo": "40 kcal/100g"},
    "orange": {"ten": "Cam", "loi_ich": "🍊 Tăng cường hệ miễn dịch.", "mon_an": "Nước cam vắt.", "calo": "47 kcal/100g"},
    "paprika": {"ten": "Ớt bột", "loi_ich": "🌶️ Giàu Vitamin E.", "mon_an": "Gia vị tẩm ướp.", "calo": "282 kcal/100g"},
    "pear": {"ten": "Lê", "loi_ich": "🍐 Thanh lọc phổi, giảm ho.", "mon_an": "Lê chưng đường phèn.", "calo": "57 kcal/100g"},
    "peas": {"ten": "Đậu Hà Lan", "loi_ich": "🫛 Đạm thực vật tốt.", "mon_an": "Cơm chiên, súp đậu.", "calo": "81 kcal/100g"},
    "pineapple": {"ten": "Dứa (Thơm)", "loi_ich": "🍍 Hỗ trợ tiêu hóa nhanh.", "mon_an": "Canh chua, nước ép.", "calo": "50 kcal/100g"},
    "pomegranate": {"ten": "Lựu", "loi_ich": "🔴 Bảo vệ tim mạch.", "mon_an": "Nước ép lựu.", "calo": "83 kcal/100g"},
    "potato": {"ten": "Khoai tây", "loi_ich": "🥔 Tinh bột chất lượng.", "mon_an": "Canh hầm, khoai chiên.", "calo": "77 kcal/100g"},
    "raddish": {"ten": "Củ cải đỏ", "loi_ich": "🧶 Hỗ trợ giải độc gan.", "mon_an": "Salad, muối chua.", "calo": "16 kcal/100g"},
    "soy beans": {"ten": "Đậu nành", "loi_ich": "🫛 Giàu protein.", "mon_an": "Sữa đậu nành, đậu hũ.", "calo": "173 kcal/100g"},
    "spinach": {"ten": "Cải bó xôi", "loi_ich": "🥬 Giàu sắt và canxi.", "mon_an": "Xào tỏi, sinh tố.", "calo": "23 kcal/100g"},
    "sweetcorn": {"ten": "Bắp ngọt", "loi_ich": "🌽 Tốt cho thị lực.", "mon_an": "Sữa bắp, chè bắp.", "calo": "86 kcal/100g"},
    "sweetpotato": {"ten": "Khoai lang", "loi_ich": "🍠 Tốt cho giảm cân.", "mon_an": "Khoai luộc, nướng.", "calo": "86 kcal/100g"},
    "tomato": {"ten": "Cà chua", "loi_ich": "🍅 Đẹp da, bảo vệ tim.", "mon_an": "Sốt cà, canh chua.", "calo": "18 kcal/100g"},
    "turnip": {"ten": "Củ cải trắng", "loi_ich": "🦯 Nhuận tràng, trị ho.", "mon_an": "Củ cải kho thịt.", "calo": "28 kcal/100g"},
    "watermelon": {"ten": "Dưa hấu", "loi_ich": "🍉 Giải nhiệt cực tốt.", "mon_an": "Nước ép.", "calo": "30 kcal/100g"}
}

@st.cache_resource
def load_model(project_id, version):
    try:
        rf = Roboflow(api_key=API_KEY_ROBOFLOW)
        project = rf.workspace().project(project_id)
        return project.version(version).model
    except:
        return None

def calculate_polygon_area(points):
    area = 0.0
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        area += points[i]['x'] * points[j]['y']
        area -= points[j]['x'] * points[i]['y']
    return abs(area) / 2.0

def bac_si_kham_benh(img):
    """Bác sĩ AI khám trái cây - Sử dụng model mới 2026"""
    try:
        # Model hiện tại ổn định nhất (hỗ trợ ảnh rất tốt)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = """Bạn là chuyên gia nông nghiệp. 
Nhìn ảnh trái cây này và trả lời cực ngắn gọn theo đúng format sau:
1. Tình trạng quả: 
2. Nguyên nhân hỏng (nếu có): 
3. Lời khuyên dùng:"""
        response = model.generate_content([prompt, img])
        return response.text.strip()
    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
            return "❌ Hệ thống Gemini đang quá tải (429). Hãy đợi 30 giây rồi thử lại nhé!"
        if "404" in error_str or "not found" in error_str:
            return "❌ Model Gemini mới nhất chưa sẵn sàng. Hãy thử lại sau 1 phút hoặc liên hệ mình nhé!"
        return f"❌ Lỗi Gemini: {str(e)}"
# =============================================================================    """Bác sĩ AI khám trái cây - ĐÃ FIX HOÀN TOÀN"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = """Bạn là chuyên gia nông nghiệp. 
Nhìn ảnh trái cây này và trả lời cực ngắn gọn theo đúng format sau:
1. Tình trạng quả: 
2. Nguyên nhân hỏng (nếu có): 
3. Lời khuyên dùng:"""
        response = model.generate_content([prompt, img])
        return response.text.strip()
    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
            return "❌ Hệ thống Gemini đang quá tải (429). Vương hãy đợi 30 giây rồi thử lại nhé!"
        if "404" in error_str or "not found" in error_str:
            return "❌ Model không tồn tại. Đã chuyển sang gemini-1.5-flash."
        return f"❌ Lỗi Gemini: {str(e)}"

# Tải model Roboflow
model_phan_loai = load_model(PROJECT_ID_1, VERSION_1)
model_do_hu = load_model(PROJECT_ID_ROT, VERSION_ROT)

#  (UI) 
st.set_page_config(page_title="AI Trái Cây Pro", page_icon="🍎", layout="wide")
with st.sidebar:
    st.header("⚙️ Cấu hình")
    # st.info(f"API Key: ...{GEMINI_API_KEY[-5:]}")
    st.success("Trạng thái: Đang hoạt động")
st.title(" Hệ Thống Giám Định Trái Cây Thông Minh")
st.write(f"Chào **bạn**, ứng dụng đã được tối ưu.")
uploaded_file = st.file_uploader(" Tải ảnh trái cây lên...", type=["jpg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='Ảnh đã tải lên', width=500)
    col1, col2, col3 = st.columns(3)
    temp_path = "temp_process.jpg"
    image.convert("RGB").save(temp_path)
    with col1:
        if st.button(" Đây là quả gì?", use_container_width=True, key="btn_detect"):
            with st.spinner('Đang nhận diện...'):
                if model_phan_loai:
                    res = model_phan_loai.predict(temp_path).json()
                    if res.get("predictions"):
                        data = res["predictions"][0]
                        label = (data.get("top") or data.get("class")).lower()
                        info = data_trai_cay.get(label, {"ten": label, "loi_ich": "Chưa có dữ liệu", "calo": "?", "mon_an": "?"})
                        
                        st.success(f"### Kết quả: {info['ten']}")
                        st.write(f"**Dinh dưỡng:** {info['loi_ich']}")
                        st.write(f"**Năng lượng:** {info['calo']}")
                        st.write(f"**Món gợi ý:** {info['mon_an']}")
                    else: 
                        st.warning("Không rõ loại quả này.")
                else: 
                    st.error("Model Roboflow không phản hồi.")

    #  ĐOÁN % HƯ HỎNG
    with col2:
        if st.button("📉 Đoán % hư hỏng", use_container_width=True, key="btn_rot"):
            with st.spinner('Đang phân tích vết hỏng...'):
                if model_do_hu:
                    res = model_do_hu.predict(temp_path, confidence=25).json()
                    preds = res.get("predictions", [])
                    if preds:
                        total_fruit_area = 0
                        total_rot_area = 0
                        for p in preds:
                            area = calculate_polygon_area(p["points"]) if "points" in p else (p["width"] * p["height"])
                            class_name = p['class'].lower()
                            if any(word in class_name for word in ["stale", "rot", "hỏng", "thối"]):
                                total_rot_area += area
                            else:
                                total_fruit_area += area
                        
                        if (total_fruit_area + total_rot_area) > 0:
                            percent = (total_rot_area / (total_fruit_area + total_rot_area)) * 100
                            st.metric("Mức độ hư hại", f"{percent:.1f}%")
                            if percent < 15: 
                                st.success("Quả này còn rất tươi!")
                            elif percent < 40: 
                                st.warning("Quả bắt đầu hỏng, nên dùng ngay.")
                            else: 
                                st.error("Quả này hỏng nặng rồi, bỏ thôi!")
                        else: 
                            st.info("Không xác định được tỷ lệ.")
                    else: 
                        st.success("Không tìm thấy vết hư hại nào!")
                else: 
                    st.error("Model phân tích hư hại chưa sẵn sàng.")

    with col3:
        if st.button("🩺 Bác sĩ AI khám", use_container_width=True, key="btn_gemini"):
            with st.spinner('Bác sĩ AI đang xem ảnh...'):
                ket_qua = bac_si_kham_benh(image)
                st.info(ket_qua)
    if os.path.exists(temp_path):
        os.remove(temp_path)
st.divider()
st.caption(" Học tập và Phát triển 2026")