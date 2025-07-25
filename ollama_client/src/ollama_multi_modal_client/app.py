import streamlit as st
import requests
import re
from PIL import Image
import io
import base64

st.set_page_config(page_title="IBKI 멀티모달 챗", layout="wide")

# --- 개인정보 검출 함수 (간단 예시) ---
def detect_personal_info(text):
    patterns = [
        r"\b\d{2,3}-\d{3,4}-\d{4}\b",  # 전화번호
        r"\b[0-9a-zA-Z._%+-]+@[0-9a-zA-Z.-]+\.[a-zA-Z]{2,}\b",  # 이메일
        r"\b\d{6}-\d{7}\b",  # 주민등록번호(간단)
        r"\b[가-힣]{2,4}\b"  # 한글 이름(매우 단순, 실제 서비스는 더 정교하게)
    ]
    for p in patterns:
        if re.search(p, text):
            return True
    return False

def check_personal_info_with_ollama(text):
    prompt = (
        f"다음 문장에 개인정보(이름, 전화번호, 이메일, 주민등록번호 등)가 포함되어 있습니까? "
        f"'{text}'. 포함되어 있으면 'YES', 아니면 'NO'만 답하세요."
    )
    payload = {
        "model": "qwen2.5vl:7b",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        answer = response.json()["response"].strip().upper()
        return answer.startswith("YES")
    except Exception as e:
        # 오류시 안전하게 YES로 처리(보수적)
        return True

# --- 스타일 (ChatGPT 유사) ---
st.markdown("""
<style>
.chat-container {
    max-width: 700px;
    margin: 0 auto;
    padding-bottom: 80px;
}
.chat-message {
    display: flex;
    margin-bottom: 16px;
}
.chat-message.user { justify-content: flex-end; }
.chat-message.bot { justify-content: flex-start; }
.bubble {
    max-width: 70%;
    padding: 16px;
    border-radius: 16px;
    font-size: 1.1rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin: 0 8px;
    word-break: break-word;
}
.bubble.user {
    background: #DCF8C6;
    color: #222;
    border-bottom-right-radius: 4px;
}
.bubble.bot {
    background: #F1F0F0;
    color: #222;
    border-bottom-left-radius: 4px;
}
.input-row {
    position: fixed;
    bottom: 0;
    left: 0; right: 0;
    background: #fff;
    padding: 16px 0 12px 0;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.04);
    z-index: 100;
}
.input-inner {
    max-width: 700px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 8px;
}
.stTextArea textarea {
    min-height: 40px !important;
    max-height: 80px !important;
}
.warning-box {
    background: #fff3cd;
    color: #856404;
    border: 1px solid #ffeeba;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 1rem;
}
.info-box {
    background: #e9f7fe;
    color: #31708f;
    border: 1px solid #bce8f1;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 1rem;
}
</style>
""", unsafe_allow_html=True)

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def generate_response(prompt, image=None):
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

# --- 세션 상태 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""
if "pending_image" not in st.session_state:
    st.session_state.pending_image = None
if "personal_info_warning" not in st.session_state:
    st.session_state.personal_info_warning = False

# --- 개인정보 안내/경고 UI ---
st.markdown(
    '<div class="info-box">⚠️ <b>개인정보 보호 안내:</b> 이름, 전화번호, 이메일, 주민등록번호 등 개인정보를 입력하지 마세요.<br>입력 시 자동으로 검출되어 안내됩니다.</div>',
    unsafe_allow_html=True
)
if st.session_state.personal_info_warning:
    st.markdown(
        '<div class="warning-box">🚨 <b>개인정보가 포함된 메시지입니다.</b><br>개인정보를 제거한 후 다시 입력해 주세요.</div>',
        unsafe_allow_html=True
    )

# --- 채팅 내역 표시 ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    image = msg.get("image")
    st.markdown(
        f'''
        <div class="chat-message {role}">
            <div class="bubble {role}">
                {content.replace('\n', '<br>')}
                {'<br><img src="data:image/png;base64,' + image + '" style="max-width:200px; margin-top:8px; border-radius:8px;" />' if image else ''}
            </div>
        </div>
        ''', unsafe_allow_html=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# --- 입력창/버튼/이미지 업로드 (하단 고정) ---
with st.container():
    st.markdown('<div class="input-row"><div class="input-inner">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="chat_image", label_visibility="collapsed")
    prompt = st.text_area(
        "",
        placeholder="메시지를 입력하세요...",
        key="chat_input",
        label_visibility="collapsed",
        height=68  # 최소 68 이상으로 변경
    )
    send = st.button("전송", key="send_btn")
    st.markdown('</div></div>', unsafe_allow_html=True)

# --- 메시지 전송 처리 ---
if send and prompt.strip():
    # Ollama로 개인정보 포함 여부 판별
    with st.spinner("개인정보 포함 여부를 확인 중..."):
        has_personal_info = check_personal_info_with_ollama(prompt)
    if has_personal_info:
        st.session_state.personal_info_warning = True
        st.session_state.pending_prompt = prompt
        st.session_state.pending_image = uploaded_file
        st.stop()
    else:
        st.session_state.personal_info_warning = False
        image_b64 = None
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            image_b64 = base64.b64encode(buffered.getvalue()).decode()
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "image": image_b64
        })
        with st.spinner("응답 생성 중..."):
            response = generate_response(prompt, Image.open(uploaded_file) if uploaded_file else None)
        st.session_state.messages.append({
            "role": "bot",
            "content": response,
            "image": None
        })
        if "chat_input" in st.session_state:
            del st.session_state["chat_input"]
        if "chat_image" in st.session_state:
            del st.session_state["chat_image"]
        st.rerun()

# --- 개인정보 경고 후 재입력 안내 ---
if st.session_state.personal_info_warning and not send:
    st.info("개인정보를 제거한 후 메시지를 다시 입력해 주세요.")

# --- 안내 메시지 (대화 시작 전) ---
if not st.session_state.messages:
    st.info("이미지와 텍스트를 입력해 대화를 시작하세요.") 