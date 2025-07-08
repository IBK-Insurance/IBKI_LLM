import streamlit as st
from PIL import Image
import io
import base64
import pandas as pd
from PyPDF2 import PdfReader
import docx
import requests

# 개인정보 정의/예시
PERSONAL_INFO_CONTEXT = """
개인정보란 이름, 주민등록번호, 연락처, 이메일 등 개인을 식별할 수 있는 정보를 의미합니다.
개인정보에는 주소, 전화번호, 계좌번호, 신용카드번호, 생년월일, 성별 등이 포함될 수 있습니다.
개인정보 보호법에 따라 개인을 식별할 수 있는 모든 정보는 보호 대상입니다.
개인정보의 예시: 김철수, 010-1234-5678, kim@email.com, 서울시 강남구, 123-45-67890
개인정보가 아닌 것: 일반적인 직업명, 나이대, 지역명(시/도 단위), 성별 등
"""

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5vl:7b"

def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_excel(file):
    df = pd.read_excel(file)
    return df.to_string(index=False)

def generate_response(prompt, image=None):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    if image:
        payload["images"] = [encode_image_to_base64(image)]
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Error: {str(e)}"

st.set_page_config(page_title="On-Device 개인정보 가드레일 시스템", layout="wide")
st.title("🔒 On-Device 개인정보 가드레일 시스템 ")

with st.sidebar:
    st.header("📁 파일 업로드")
    uploaded_file = st.file_uploader(
        "이미지, PDF, DOCX, Excel, TXT 파일을 업로드하세요",
        type=["jpg", "jpeg", "png", "pdf", "docx", "xlsx", "txt"]
    )

    st.markdown("---")
    st.info("또는 아래에서 직접 텍스트를 입력할 수 있습니다.")

user_text = ""
image = None

if uploaded_file is not None:
    filetype = uploaded_file.type
    filename = uploaded_file.name.lower()
    if filetype.startswith("image/"):
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", use_column_width=True)
    elif filename.endswith(".pdf"):
        user_text = extract_text_from_pdf(uploaded_file)
        st.text_area("PDF에서 추출된 텍스트", user_text, height=200)
    elif filename.endswith(".docx"):
        user_text = extract_text_from_docx(uploaded_file)
        st.text_area("DOCX에서 추출된 텍스트", user_text, height=200)
    elif filename.endswith(".xlsx"):
        user_text = extract_text_from_excel(uploaded_file)
        st.text_area("Excel에서 추출된 텍스트", user_text, height=200)
    elif filename.endswith(".txt"):
        user_text = uploaded_file.read().decode("utf-8")
        st.text_area("TXT 파일 내용", user_text, height=200)
    else:
        st.error("지원하지 않는 파일 형식입니다.")

if not user_text and not image:
    user_text = st.text_area("직접 텍스트 입력", "", height=200)

if st.button("🚀 개인정보 포함여부 판별"):
    if not user_text and not image:
        st.warning("분석할 텍스트 또는 이미지를 입력/업로드하세요.")
    else:
        # 프롬프트 구성
        prompt = f"""다음은 개인정보의 정의와 예시입니다:
{PERSONAL_INFO_CONTEXT}

아래 입력(텍스트 또는 이미지)에 개인정보가 포함되어 있으면 '포함됨', 포함되어 있지 않으면 '포함되지 않음'이라고만 답하세요.

입력:
{user_text if user_text else '[이미지 첨부]'}
"""
        with st.spinner("분석 중..."):
            result = generate_response(prompt, image)
        if "포함됨" in result:
            st.error("🚨 개인정보가 포함되어 있습니다!")
        elif "포함되지 않음" in result:
            st.success("✅ 개인정보가 포함되어 있지 않습니다!")
        else:
            st.warning("⚠️ 판별 결과를 확인할 수 없습니다.")
        st.markdown("**결과:**")
        st.code(result)

st.markdown("---")
st.markdown("""
- 이미지, PDF, DOCX, Excel, 텍스트 모두 지원
- Local sLLM 모델이 실행 중이어야 함
- 판별 기준: 이름, 연락처, 이메일, 주소, 계좌번호 등
""") 