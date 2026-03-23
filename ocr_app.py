import streamlit as st
import requests
import base64
from PIL import Image
import pytesseract

st.set_page_config(page_title="OCR Chứng từ với API", layout="wide")
st.title("OCR Chứng từ với Google Vision API")

st.markdown("""
#### Hướng dẫn:
1. Nhập API key Google Cloud Vision.
2. Upload ảnh chứng từ (PNG, JPG, JPEG).
3. Nhấn nút để nhận text từ OCR.
""")

api_key = st.text_input("Nhập API key Google Cloud Vision:", type="password", value="AIzaSyDG8YapLY4H_jCi9eTIWeoa102VcHZUUi4")
uploaded_file = st.file_uploader("Upload ảnh chứng từ:", type=["png", "jpg", "jpeg"])

def ocr_with_vision(image_bytes, api_key):
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    headers = {"Content-Type": "application/json"}
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    data = {
        "requests": [
            {
                "image": {"content": image_base64},
                "features": [{"type": "TEXT_DETECTION"}]
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            text_annotations = result.get("responses", [{}])[0].get("textAnnotations", [])
            if text_annotations:
                return text_annotations[0]["description"]
            else:
                return "Không tìm thấy text trong ảnh."
        elif response.status_code == 403:
            error_details = response.json() if response.text else {}
            return f"Lỗi 403 - API key không hợp lệ hoặc chưa được kích hoạt Vision API.\n\nChi tiết: {error_details.get('error', {}).get('message', 'API key không có quyền truy cập')}\n\nHãy kiểm tra:\n1. API key có đúng không\n2. Google Cloud Vision API đã được kích hoạt\n3. Billing đã được bật"
        else:
            return f"Lỗi API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Lỗi khi gọi API: {e}"

def ocr_local(image):
    try:
        # Kiểm tra xem tesseract có được cài đặt không
        import subprocess
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            return "Lỗi: Tesseract OCR chưa được cài đặt.\n\nVui lòng cài đặt Tesseract:\n1. Tải từ: https://github.com/UB-Mannheim/tesseract/wiki\n2. Cài đặt và thêm vào PATH\n3. Restart app"
        
        text = pytesseract.image_to_string(image, lang='eng')
        return text.strip() if text.strip() else "Không tìm thấy text trong ảnh."
    except Exception as e:
        return f"Lỗi OCR: {e}"

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh đã upload", width=400)
        
        if st.button("OCR chứng từ"):
            with st.spinner("Đang OCR..."):
                if api_key.strip():  # Nếu có API key, dùng Google Vision API
                    image_bytes = uploaded_file.getvalue()
                    ocr_text = ocr_with_vision(image_bytes, api_key)
                else:  # Nếu không có API key, dùng OCR local
                    ocr_text = ocr_local(image)
            st.subheader("Kết quả OCR:")
            st.text_area("Text từ chứng từ:", ocr_text, height=300)
    except Exception as e:
        st.error(f"Lỗi xử lý ảnh: {e}")
else:
    st.info("Upload ảnh để bắt đầu OCR.")