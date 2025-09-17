"""
LLM 서비스 모듈
- Ollama LLM 초기화 및 관리
- 개인정보 판별 로직
- 이미지 텍스트 추출
"""

import streamlit as st
from langchain.llms import Ollama
from PIL import Image
import io
import base64
import logging

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

def check_personal_info(text):
    """개인정보 포함여부 판별"""
    llm = initialize_llm()
    if llm:
        try:
            prompt = f"""
다음 텍스트에 개인정보가 포함되어 있는지 판별해주세요.

{PERSONAL_INFO_CRITERIA}

분석할 텍스트:
{text}

위 텍스트에 개인정보가 포함되어 있으면 '포함됨'이라고 답하고, 어떤 개인정보가 포함되어 있는지 구체적으로 예시(문장/항목)를 함께 출력하세요.
포함되어 있지 않으면 '포함되지 않음'이라고만 답하세요.
"""
            result = llm.invoke(prompt)
            return result
        except Exception as e:
            st.error(f"판별 중 오류 발생: {str(e)}")
            return "오류 발생"
    return "시스템 초기화 실패"

def extract_text_from_image_llm(image: Image.Image):
    """이미지에서 텍스트 추출 (멀티모달 LLM 활용)"""
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

def check_personal_info_image(image: Image.Image):
    """이미지에서 개인정보 포함여부 판별 (멀티모달 LLM 활용)"""
    # 1. 이미지에서 텍스트 추출
    extracted_text = extract_text_from_image_llm(image)
    if not extracted_text or extracted_text.strip() in ["오류 발생", "시스템 초기화 실패", "텍스트 없음"]:
        return "이미지에서 개인정보를 판별할 텍스트를 추출하지 못했습니다."
    # 2. 추출된 텍스트로 개인정보 판별
    return check_personal_info(extracted_text)
