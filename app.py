import streamlit as st
from roboflow import Roboflow
from PIL import Image
import time
import google.generativeai as genai
import os
import math

# --- 1. CẤU HÌNH HỆ THỐNG ---
API_KEY_ROBOFLOW = "EkNBEpyZvjbdWCARPUuj" 

# Model 1: Nhận diện loại quả (Classification)
PROJECT_ID_1 = "myfirstproject-vbszv"
VERSION_1 = 1 # Kiểm tra lại version trên Roboflow của bạn

# Model 2: Nhận diện độ hư (Instance Segmentation - Fresh and stale fruits)
PROJECT_ID_ROT = "fresh-and-stale-fruits-vjs0a" # Thay ID chính xác của project này vào đây
VERSION_ROT = 1

GEMINI_API_KEY = "AIzaSyBeItirrb559l77j8oOhstAyRhyMXmJy0c"
genai.configure(api_key=GEMINI_API_KEY)

MIN_CONFIDENCE = 0.50

  # --- 2. KHO DỮ LIỆU DINH DƯỠNG CHI TIẾT ---
data_trai_cay = {
      "apple": {"ten": "Táo", "loi_ich": "🍎 Giàu chất xơ và Vitamin C. Giúp giảm nguy cơ tiểu đường và tốt cho tim mạch.", "mon_an": "Salad táo, bánh pie táo, nước ép táo.", "calo": "52 kcal/100g"},
      "banana": {"ten": "Chuối", "loi_ich": "🍌 Cung cấp Kali dồi dào, giúp ổn định huyết áp và cung cấp năng lượng nhanh.", "mon_an": "Chè chuối, chuối nếp nướng, sinh tố chuối.", "calo": "89 kcal/100g"},
      "beetroot": {"ten": "Củ dền", "loi_ich": "🩸 Giúp hạ huyết áp, cải thiện lưu thông máu và tăng sức bền thể thao.", "mon_an": "Canh củ dền hầm xương, nước ép mix, salad.", "calo": "43 kcal/100g"},
      "bell pepper": {"ten": "Ớt chuông", "loi_ich": "🫑 Lượng Vitamin C cực cao, giúp sáng mắt và đẹp da.", "mon_an": "Ớt chuông xào bò, cơm chiên, nướng BBQ.", "calo": "20-30 kcal/100g"},
      "cabbage": {"ten": "Bắp cải", "loi_ich": "🥬 Chứa nhiều Vitamin K giúp cải thiện sự tập trung và chức năng não.", "mon_an": "Bắp cải cuộn thịt, xào tỏi, làm kim chi.", "calo": "25 kcal/100g"},
      "capsicum": {"ten": "Ớt chuông (Ớt Đà Lạt)", "loi_ich": "🌶️ Giàu chất chống oxy hóa, hỗ trợ hệ miễn dịch và giảm viêm.", "mon_an": "Salad Hy Lạp, xào thập cẩm, ớt nhồi thịt.", "calo": "20 kcal/100g"},
      "carrot": {"ten": "Cà rốt", "loi_ich": "🥕 Nguồn Beta-carotene tuyệt vời giúp mắt sáng và bảo vệ da.", "mon_an": "Nước ép cà rốt, kho bò, salad trộn.", "calo": "41 kcal/100g"},
      "cauliflower": {"ten": "Súp lơ trắng", "loi_ich": "🥦 Giàu chất xơ và Sulforaphane hỗ trợ ngăn ngừa ung thư.", "mon_an": "Súp lơ xào, súp kem súp lơ.", "calo": "25 kcal/100g"},
      "chilli pepper": {"ten": "Ớt cay", "loi_ich": "🔥 Chứa Capsaicin thúc đẩy trao đổi chất và giảm đau tự nhiên.", "mon_an": "Làm nước chấm, gia vị tẩm ướp, sa tế.", "calo": "40 kcal/100g"},
      "corn": {"ten": "Bắp (Ngô)", "loi_ich": "🌽 Tốt cho tiêu hóa nhờ lượng chất xơ dồi dào và cung cấp năng lượng.", "mon_an": "Bắp luộc, bắp xào, súp bắp.", "calo": "86 kcal/100g"},
      "cucumber": {"ten": "Dưa leo", "loi_ich": "🥒 Chứa 95% nước giúp giải độc, cấp ẩm cho da và thanh lọc cơ thể.", "mon_an": "Ăn sống, salad dưa chuột, làm mask dưỡng da.", "calo": "15 kcal/100g"},
      "eggplant": {"ten": "Cà tím", "loi_ich": "🍆 Bảo vệ tế bào não và hỗ trợ kiểm soát đường huyết.", "mon_an": "Cà tím nướng mỡ hành, cà tím xào tỏi.", "calo": "25 kcal/100g"},
      "garlic": {"ten": "Tỏi", "loi_ich": "🧄 Kháng sinh tự nhiên, phòng ngừa cảm cúm và tốt cho huyết áp.", "mon_an": "Gia vị xào, nước mắm tỏi ớt, tỏi ngâm giấm.", "calo": "149 kcal/100g"},
      "ginger": {"ten": "Gừng", "loi_ich": "🫚 Giảm buồn nôn, hỗ trợ tiêu hóa và giữ ấm cơ thể.", "mon_an": "Trà gừng, gà kho gừng.", "calo": "80 kcal/100g"},
      "grapes": {"ten": "Nho", "loi_ich": "🍇 Chống lão hóa và bảo vệ sức khỏe tim mạch.", "mon_an": "Ăn tươi, mứt nho, nước ép nho.", "calo": "67 kcal/100g"},
      "jalapeno": {"ten": "Ớt Jalapeno", "loi_ich": "🌶️ Giúp giảm cân bằng cách đốt cháy calo và cải thiện lưu thông máu.", "mon_an": "Pizza, bánh mì Tacos, ớt ngâm chua.", "calo": "29 kcal/100g"},
      "kiwi": {"ten": "Kiwi", "loi_ich": "🥝 Vitamin C cực cao, tăng đề kháng và hỗ trợ giấc ngủ.", "mon_an": "Sinh tố kiwi, trang trí bánh kem.", "calo": "61 kcal/100g"},
      "lemon": {"ten": "Chanh vàng", "loi_ich": "🍋 Giải độc gan, sạch đường tiêu hóa và làm thơm hơi thở.", "mon_an": "Nước chanh mật ong, gia vị salad.", "calo": "29 kcal/100g"},
      "lettuce": {"ten": "Xà lách", "loi_ich": "🥗 Giúp an thần, ngủ ngon và thanh nhiệt cơ thể.", "mon_an": "Salad trộn, ăn kèm bánh xèo.", "calo": "15 kcal/100g"},
      "mango": {"ten": "Xoài", "loi_ich": "🥭 Giàu Vitamin A cho mắt và enzyme hỗ trợ tiêu hóa.", "mon_an": "Xoài chín ăn tươi, gỏi xoài xanh, sinh tố.", "calo": "60 kcal/100g"},
      "onion": {"ten": "Hành tây", "loi_ich": "🧅 Kháng viêm, hỗ trợ sức khỏe xương khớp và tim mạch.", "mon_an": "Xào thịt bò, súp hành tây.", "calo": "40 kcal/100g"},
      "orange": {"ten": "Cam", "loi_ich": "🍊 Tăng cường hệ miễn dịch, giúp da săn chắc nhờ collagen.", "mon_an": "Nước cam vắt, salad vị cam.", "calo": "47 kcal/100g"},
      "paprika": {"ten": "Ớt bột Paprika", "loi_ich": "🌶️ Giàu Vitamin E và sắt, giúp cải thiện sức khỏe máu.", "mon_an": "Gia vị ướp thịt, rắc khoai tây chiên.", "calo": "282 kcal/100g"},
      "pear": {"ten": "Lê", "loi_ich": "🍐 Tính mát, giúp nhuận tràng, giảm ho và thanh lọc phổi.", "mon_an": "Lê chưng đường phèn, salad lê.", "calo": "57 kcal/100g"},
      "peas": {"ten": "Đậu Hà Lan", "loi_ich": "🫛 Nguồn đạm thực vật tốt cho cơ bắp và tiêu hóa.", "mon_an": "Cơm chiên Dương Châu, súp đậu.", "calo": "81 kcal/100g"},
      "pineapple": {"ten": "Dứa (Thơm)", "loi_ich": "🍍 Enzyme Bromelain giúp tiêu hóa nhanh và giảm viêm.", "mon_an": "Canh chua, dứa xào mực, nước ép.", "calo": "50 kcal/100g"},
      "pomegranate": {"ten": "Lựu", "loi_ich": "🔴 Chống oxy hóa cực mạnh, bảo vệ tim mạch.", "mon_an": "Nước ép lựu, trộn salad.", "calo": "83 kcal/100g"},
      "potato": {"ten": "Khoai tây", "loi_ich": "🥔 Cung cấp tinh bột chất lượng cao và giàu Kali.", "mon_an": "Canh hầm xương, khoai tây chiên.", "calo": "77 kcal/100g"},
      "raddish": {"ten": "Củ cải đỏ", "loi_ich": "🧶 Nhiều chất xơ, hỗ trợ giải độc gan và thận.", "mon_an": "Salad củ cải, muốn chua.", "calo": "16 kcal/100g"},
      "soy beans": {"ten": "Đậu nành", "loi_ich": "🫛 Giàu protein và isoflavone tốt cho nội tiết tố.", "mon_an": "Sữa đậu nành, đậu hũ.", "calo": "173 kcal/100g"},
      "spinach": {"ten": "Cải bó xôi", "loi_ich": "🥬 Giàu sắt và canxi, bổ máu và chắc xương.", "mon_an": "Xào tỏi, làm sinh tố xanh.", "calo": "23 kcal/100g"},
      "sweetcorn": {"ten": "Bắp ngọt", "loi_ich": "🌽 Giàu Lutein tốt cho thị lực.", "mon_an": "Sữa bắp, bắp luộc, chè bắp.", "calo": "86 kcal/100g"},
      "sweetpotato": {"ten": "Khoai lang", "loi_ich": "🍠 Tinh bột hấp thụ chậm, tốt cho người giảm cân.", "mon_an": "Khoai lang luộc, nướng.", "calo": "86 kcal/100g"},
      "tomato": {"ten": "Cà chua", "loi_ich": "🍅 Lycopene giúp bảo vệ tim mạch và đẹp da.", "mon_an": "Đậu hũ sốt cà, canh chua.", "calo": "18 kcal/100g"},
      "turnip": {"ten": "Củ cải trắng", "loi_ich": "🦯 Nhuận tràng, trị ho và hỗ trợ tiêu hóa.", "mon_an": "Củ cải kho thịt, nấu canh xương.", "calo": "28 kcal/100g"},
      "watermelon": {"ten": "Dưa hấu", "loi_ich": "🍉 Giải nhiệt cực tốt, giàu chất chống oxy hóa.", "mon_an": "Nước ép, salad trái cây.", "calo": "30 kcal/100g"}
  }

 @st.cache_resource
def load_model(project_id, version):
    rf = Roboflow(api_key=API_KEY_ROBOFLOW)
    project = rf.workspace().project(project_id)
    return project.version(version).model

def calculate_polygon_area(points):
    """Tính diện tích đa giác bằng công thức Shoelace"""
    area = 0.0
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        area += points[i]['x'] * points[j]['y']
        area -= points[j]['x'] * points[i]['y']
    return abs(area) / 2.0

def get_best_available_model():
    try:
        uu_tien = ['gemini-1.5-flash', 'gemini-1.5-pro']
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for model_name in uu_tien:
            if any(model_name in m for m in available_models): return model_name
        return 'gemini-1.5-flash'
    except: return 'gemini-1.5-flash'

def bac_si_kham_benh(img):
    working_model = get_best_available_model()
    try:
        gemini_model = genai.GenerativeModel(working_model)
        prompt = "Bạn là chuyên gia nông nghiệp. Nhìn ảnh và trả lời ngắn gọn: 1.Tình trạng, 2.Lý do, 3.Lời khuyên."
        response = gemini_model.generate_content([prompt, img])
        return response.text
    except Exception as e: return f"❌ Lỗi: {str(e)}"

# Tải 2 model Roboflow
model_phan_loai = load_model(PROJECT_ID_1, VERSION_1)
model_do_hu = load_model(PROJECT_ID_ROT, VERSION_ROT)

# --- 4. GIAO DIỆN NGƯỜI DÙNG (UI) ---
st.set_page_config(page_title="AI Trái Cây Pro", page_icon="🍎", layout="wide")
st.title("🍎 Hệ Thống Giám Định Trái Cây Thông Minh")
st.write(f"Xin chào **Vương**, hệ thống đã sẵn sàng tích hợp 2 model nhận diện.")

uploaded_file = st.file_uploader("📤 Tải ảnh trái cây lên...", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='Ảnh đầu vào', width=500)
    
    # Chia làm 3 cột cho 3 chức năng
    col1, col2, col3 = st.columns(3)
    
    temp_path = "temp_process.jpg"
    image.convert("RGB").save(temp_path)

    with col1:
        if st.button("🔍 Đây là quả gì?", use_container_width=True):
            with st.spinner('Đang nhận diện loại...'):
                res = model_phan_loai.predict(temp_path).json()
                if res.get("predictions"):
                    data = res["predictions"][0]
                    label = (data.get("top") or data.get("class")).lower()
                    info = data_trai_cay.get(label, {"ten": label, "loi_ich": "Chưa có dữ liệu", "calo": "?", "mon_an": "?"})
                    st.success(f"### Kết quả: {info['ten']}")
                    st.write(f"Độ tin cậy: {data['confidence']:.1%}")
                    with st.expander("Chi tiết dinh dưỡng"):
                        st.write(info['loi_ich'])
                else: st.warning("Không rõ loại quả.")

    with col2:
        if st.button("📉 Đoán % hư hỏng", use_container_width=True):
            with st.spinner('Đang phân tích vết hư...'):
                res = model_do_hu.predict(temp_path).json()
                preds = res.get("predictions", [])
                
                if preds:
                    total_fruit_area = 0
                    total_rot_area = 0
                    
                    for p in preds:
                        # Giả sử class 'stale' hoặc 'rot' là vùng hư
                        # Class 'fresh' hoặc tên quả là vùng lành lặn
                        points = p.get("points", [])
                        if not points: continue
                        
                        area = calculate_polygon_area(points)
                        
                        if p['class'].lower() in ['stale', 'rot', 'damaged', 'hu']:
                            total_rot_area += area
                        else:
                            total_fruit_area += area # Vùng trái cây nói chung
                    
                    # Tính toán tỷ lệ
                    if total_fruit_area > 0:
                        # Nếu model chỉ khoanh vùng hư trên quả
                        percent = (total_rot_area / total_fruit_area) * 100
                        # Giới hạn max 100%
                        percent = min(percent, 100.0)
                        
                        st.metric("Mức độ hư hại", f"{percent:.1f}%")
                        if percent < 5: st.success("Trái cây rất tươi!")
                        elif percent < 30: st.warning("Bắt đầu có dấu hiệu hư hỏng.")
                        else: st.error("Trái cây đã hỏng nặng!")
                    else:
                        st.info("Không tìm thấy vết hư rõ rệt hoặc vùng trái cây.")
                else:
                    st.success("Chúc mừng! Không phát hiện vết hư nào.")

    with col3:
        if st.button("🩺 Bác sĩ AI khám", use_container_width=True):
            with st.spinner('Gemini đang khám...'):
                st.info(bac_si_kham_benh(image))

    if os.path.exists(temp_path): os.remove(temp_path)

st.divider()
st.caption("Giao diện tối ưu cho Vương - 2026")