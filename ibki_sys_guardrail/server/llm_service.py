"""
LLM 서비스 모듈
- Ollama LLM 초기화 및 관리
- 개인정보 판별 로직
- 이미지 텍스트 추출
"""

import streamlit as st
from langchain_community.llms import Ollama
from PIL import Image
import io
import base64
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from ibki_sys_guardrail.server.pii_detector import detect, extract

# 개인정보 판별 기준
PERSONAL_INFO_CRITERIA = """
개인정보의 정의:
- 이름, 주민등록번호, 연락처, 이메일, 주소, 계좌번호, 신용카드번호, 생년월일 등 개인을 식별할 수 있는 정보
- 개인정보 보호법에 따라 개인을 식별할 수 있는 모든 정보

개인정보가 아닌 것:
- 일반적인 직업명, 나이대, 지역명(시/도 단위), 성별 등
"""

def _load_ollama_env():
    """ibki_sys_guardrail/.env에서 LLM 설정 로드 후 (model, base_url) 반환"""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path)
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    text_model = os.getenv("TEXT_LLM_MODEL", "gpt-oss:20b")
    vision_model = os.getenv("VISION_LLM_MODEL", "qwen2.5vl:7b")
    return text_model, vision_model, base_url


@st.cache_resource
def initialize_text_llm():
    """텍스트 전용 LLM 초기화 (환경변수 TEXT_LLM_MODEL)"""
    try:
        text_model, _, base_url = _load_ollama_env()
        llm = Ollama(model=text_model, base_url=base_url)
        return llm
    except Exception as e:
        st.error(f"텍스트 LLM 초기화 실패: {str(e)}")
        return None

@st.cache_resource
def initialize_vision_llm():
    """멀티모달/비전 LLM 초기화 (환경변수 VISION_LLM_MODEL)"""
    try:
        _, vision_model, base_url = _load_ollama_env()
        llm = Ollama(model=vision_model, base_url=base_url)
        return llm
    except Exception as e:
        st.error(f"비전 LLM 초기화 실패: {str(e)}")
        return None

def check_personal_info(text):
    """개인정보 포함여부 판별 (정규식 패턴 우선, LLM 보조)"""
    # 1단계: 정규식 패턴으로 개인정보 탐지
    regex_matches = detect(text)
    
    if regex_matches:
        # 정규식으로 개인정보가 탐지된 경우
        detected_types = {}
        for match in regex_matches:
            pii_type = match["type"]
            if pii_type not in detected_types:
                detected_types[pii_type] = []
            detected_types[pii_type].append(match["value"])
        
        # 탐지된 개인정보 유형별로 결과 구성
        result_parts = ["포함됨"]
        for pii_type, values in detected_types.items():
            type_names = {
                "rrn": "주민등록번호",
                "name": "성명", 
                "account": "계좌번호",
                "phone": "전화번호",
                "email": "이메일",
                "address": "주소"
            }
            type_name = type_names.get(pii_type, pii_type)
            unique_values = list(set(values))  # 중복 제거
            result_parts.append(f"{type_name}: {', '.join(unique_values[:3])}")  # 최대 3개만 표시
        
        return "\n".join(result_parts)
    
    # 2단계: 정규식으로 탐지되지 않은 경우 LLM으로 추가 탐지
    llm = initialize_text_llm()
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
            st.error(f"LLM 판별 중 오류 발생: {str(e)}")
            return "오류 발생"
    return "시스템 초기화 실패"

def extract_text_from_image_llm(image: Image.Image):
    """이미지에서 텍스트 추출 (멀티모달 LLM 활용)"""
    llm = initialize_vision_llm()
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
    # 2. 추출된 텍스트로 개인정보 판별 (정규식 우선, LLM 보조)
    return check_personal_info(extracted_text)
