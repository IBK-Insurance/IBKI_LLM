import streamlit as st
import requests
import json
from PIL import Image
import io
import base64

# 페이지 설정
st.set_page_config(
    page_title="IBKI 로컬 멀티모달 대화",
    #page_icon="🤖",
    layout="wide"
)

# CSS 스타일 적용
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .response-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 1rem;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-size: 1.1rem;
        line-height: 1.6;
        color: #2c3e50;
    }
    .response-box p {
        margin-bottom: 1rem;
    }
    .response-box strong {
        color: #1a73e8;
    }
    .response-box code {
        background-color: #e9ecef;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: monospace;
    }
    .response-box ul, .response-box ol {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }
    .response-box li {
        margin-bottom: 0.5rem;
    }
    .response-box blockquote {
        border-left: 4px solid #1a73e8;
        padding-left: 1rem;
        margin-left: 0;
        color: #5f6368;
    }
</style>
""", unsafe_allow_html=True)

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def encode_image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def generate_response(prompt, image=None):
    """Generate response from Ollama API"""
    payload = {
        "model": "qwen2.5vl:7b",
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

# 사이드바 설정
with st.sidebar:
    st.title("IBKI 로컬 멀티모달 대화")
    st.markdown("---")
    st.markdown("### 사용 방법")
    st.markdown("""
    1. 이미지를 업로드하세요
    2. 질문을 입력하세요
    3. '생성' 버튼을 클릭하세요
    """)
    st.markdown("---")
    st.markdown("### 지원 형식")
    st.markdown("- 이미지: JPG, JPEG, PNG")
    st.markdown("---")
    st.markdown("### 주의사항")
    st.markdown("- 로컬 LLM 서버가 실행 중이어야 합니다")
    st.markdown("- 이미지 크기가 너무 크면 처리 시간이 길어질 수 있습니다")

# 메인 컨텐츠
st.title("IBKI 로컬 멀티모달 대화")
st.markdown("이미지와 텍스트를 함께 처리할 수 있는 멀티모달 대화 인터페이스입니다.")

# 두 컬럼으로 레이아웃 분할
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("이미지 업로드")
    uploaded_file = st.file_uploader("이미지를 선택하세요", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", use_column_width=True)

with col2:
    st.subheader("질문 입력")
    prompt = st.text_area("이미지에 대해 질문해보세요", height=150)
    
    if st.button("생성", key="generate"):
        if not prompt:
            st.warning("질문을 입력해주세요.")
        else:
            with st.spinner("응답을 생성하는 중..."):
                response = generate_response(prompt, image if uploaded_file else None)
                st.markdown("### 응답")
                formatted_response = response.replace('\n', '  \n')  # 줄바꿈 유지
                st.markdown(f'<div class="response-box">{formatted_response}</div>', unsafe_allow_html=True)

# 상태 표시
if uploaded_file is None:
    st.info("이미지를 업로드하면 멀티모달 대화를 시작할 수 있습니다.") 