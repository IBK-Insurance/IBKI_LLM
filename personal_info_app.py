import streamlit as st
from PyPDF2 import PdfReader
import docx
import tempfile
import os
from langchain.llms import Ollama
from PIL import Image  # 이미지 처리를 위해 추가
import io
import base64

# 페이지 설정
st.set_page_config(
    page_title="개인정보 포함여부 판별기",
    page_icon="🔒",
    layout="wide"
)

# 개인정보 판별 기준
PERSONAL_INFO_CRITERIA = """
개인정보의 정의:
- 이름, 주민등록번호, 연락처, 이메일, 주소, 계좌번호, 신용카드번호, 생년월일 등 개인을 식별할 수 있는 정보
- 개인정보 보호법에 따라 개인을 식별할 수 있는 모든 정보

개인정보가 아닌 것:
- 일반적인 직업명, 나이대, 지역명(시/도 단위), 성별 등
"""

@st.cache_resource
def initialize_llm():
    """LLM 초기화 (캐시됨)"""
    try:
        llm = Ollama(model="qwen2.5vl:7b", base_url="http://localhost:11434")
        return llm
    except Exception as e:
        st.error(f"LLM 초기화 실패: {str(e)}")
        return None

def extract_text_from_pdf(file):
    """PDF 파일에서 텍스트 추출"""
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"PDF 텍스트 추출 실패: {str(e)}")
        return ""

def extract_text_from_docx(file):
    """DOCX 파일에서 텍스트 추출"""
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"DOCX 텍스트 추출 실패: {str(e)}")
        return ""

def check_personal_info(text):
    """개인정보 포함여부 판별"""
    llm = initialize_llm()
    if llm:
        try:
            # 개인정보 판별을 위한 프롬프트
            prompt = f"""
다음 텍스트에 개인정보가 포함되어 있는지 판별해주세요.

{PERSONAL_INFO_CRITERIA}

분석할 텍스트:
{text}

위 텍스트에 개인정보가 포함되어 있으면 '포함됨', 포함되어 있지 않으면 '포함되지 않음'이라고만 답하세요.
"""
            result = llm.invoke(prompt)
            return result
        except Exception as e:
            st.error(f"판별 중 오류 발생: {str(e)}")
            return "오류 발생"
    return "시스템 초기화 실패"

# 이미지 판별 함수 추가
def check_personal_info_image(image: Image.Image):
    """이미지에서 개인정보 포함여부 판별 (멀티모달 LLM 활용)"""
    # 1. 이미지에서 텍스트 추출
    extracted_text = extract_text_from_image_llm(image)
    if not extracted_text or extracted_text.strip() in ["오류 발생", "시스템 초기화 실패", "텍스트 없음"]:
        return "이미지에서 개인정보를 판별할 텍스트를 추출하지 못했습니다."
    # 2. 추출된 텍스트로 개인정보 판별
    return check_personal_info(extracted_text)

def extract_text_from_image_llm(image: Image.Image):
    llm = initialize_llm()
    if llm:
        try:
            prompt = (
                "<image>\n"
                "이 이미지에서 읽을 수 있는 모든 텍스트를 추출해서 출력해줘. "
                "텍스트가 없으면 '텍스트 없음'이라고 답해줘."
            )
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            img_b64 = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
            result = llm.invoke(prompt, images=[img_b64])
            return result
        except Exception as e:
            st.error(f"이미지 텍스트 추출 중 오류 발생: {str(e)}")
            return "오류 발생"
    return "시스템 초기화 실패"

# 메인 UI
st.title("🔒 개인정보 포함여부 판별기")
st.markdown("---")

# 사이드바 - 파일 업로드
with st.sidebar:
    st.header("📁 파일 업로드")
    uploaded_file = st.file_uploader(
        "PDF, DOCX, TXT, PNG, JPG, JPEG 파일을 업로드하세요",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        help="지원 형식: PDF, DOCX, TXT, PNG, JPG, JPEG"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ {uploaded_file.name} 업로드 완료")
        file_size = uploaded_file.size / 1024  # KB
        st.info(f"파일 크기: {file_size:.1f} KB")

# 텍스트/이미지 입력 분기
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📄 텍스트 입력")
    user_text = ""
    user_image = None
    file_type = None
    image_extracted_text = None  # 이미지에서 추출된 텍스트

    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            user_text = extract_text_from_pdf(uploaded_file)
            file_type = "text"
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            user_text = extract_text_from_docx(uploaded_file)
            file_type = "text"
        elif uploaded_file.type == "text/plain":
            user_text = uploaded_file.read().decode("utf-8")
            file_type = "text"
        elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
            user_image = Image.open(uploaded_file)
            file_type = "image"
            # 이미지에서 텍스트 추출 (LLM 활용)
            with st.spinner("이미지에서 텍스트 추출 중..."):
                image_extracted_text = extract_text_from_image_llm(user_image)
        else:
            st.error("지원하지 않는 파일 형식입니다.")
            user_text = ""
            file_type = None
    else:
        user_text = st.text_area(
            "직접 텍스트를 입력하세요",
            height=300,
            placeholder="개인정보 포함여부를 확인할 텍스트를 입력하세요..."
        )
        file_type = "text" if user_text else None
    
    # 텍스트 미리보기 (파일 업로드 시)
    if uploaded_file is not None and user_text:
        with st.expander("📋 추출된 텍스트 미리보기", expanded=False):
            st.text_area("텍스트", user_text, height=200, disabled=True)
    if uploaded_file is not None and user_image is not None:
        with st.expander("🖼️ 업로드된 이미지 미리보기", expanded=False):
            st.image(user_image, caption="업로드 이미지", use_column_width=True)
        if image_extracted_text:
            with st.expander("🖼️ 이미지에서 추출된 텍스트 미리보기", expanded=False):
                st.text_area("이미지 추출 텍스트", image_extracted_text, height=200, disabled=True)

with col2:
    st.header("🔍 분석 결과")
    if st.button("🚀 개인정보 포함여부 판별", type="primary", use_container_width=True):
        if (file_type == "text" and user_text and user_text.strip()) or (file_type == "image" and user_image is not None):
            with st.spinner("분석 중..."):
                if file_type == "text":
                    result = check_personal_info(user_text.strip())
                elif file_type == "image":
                    result = check_personal_info_image(user_image)
                else:
                    result = "분석할 데이터가 없습니다."
            # 결과 표시
            if "포함됨" in result:
                st.error("🚨 개인정보가 포함되어 있습니다!")
                st.markdown("**결과:** 포함됨")
            elif "포함되지 않음" in result:
                st.success("✅ 개인정보가 포함되어 있지 않습니다!")
                st.markdown("**결과:** 포함되지 않음")
            else:
                st.warning("⚠️ 판별 결과를 확인할 수 없습니다.")
                st.markdown(f"**결과:** {result}")
            with st.expander("📊 상세 분석 결과"):
                st.code(result)
        else:
            st.warning("⚠️ 분석할 텍스트나 이미지가 없습니다.")

# 하단 정보
st.markdown("---")
st.markdown("""
### 📋 사용 방법
1. **파일 업로드**: PDF, DOCX, TXT, PNG, JPG, JPEG 파일을 사이드바에서 업로드
2. **직접 입력**: 메인 화면에서 텍스트를 직접 입력
3. **분석 실행**: "개인정보 포함여부 판별" 버튼 클릭

### 🔍 판별 기준
- **개인정보**: 이름, 주민등록번호, 연락처, 이메일, 주소, 계좌번호 등
- **개인정보 아님**: 일반적인 직업명, 나이대, 지역명(시/도 단위) 등

### ⚠️ 주의사항
- 이 도구는 참고용이며, 법적 판단의 근거로 사용하지 마세요
- 실제 개인정보 처리 시에는 관련 법규를 준수하세요
""")

# 시스템 상태 확인
with st.sidebar:
    st.markdown("---")
    st.header("⚙️ 시스템 상태")
    
    # Ollama 연결 상태 확인
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            st.success("✅ Ollama 서버 연결됨")
        else:
            st.error("❌ Ollama 서버 연결 실패")
    except:
        st.error("❌ Ollama 서버 연결 실패")
        st.info("Ollama 서버가 실행 중인지 확인하세요") 