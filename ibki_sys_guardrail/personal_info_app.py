import streamlit as st
import logging

# Client 모듈 import
from ibki_sys_guardrail.client.text_input_section import render_text_input_section
from ibki_sys_guardrail.client.image_input_section import render_image_input_section
from ibki_sys_guardrail.client.chat_section import render_chat_section
from ibki_sys_guardrail.client.ui_components import display_system_status, display_usage_guide

# Server 모듈 import
from ibki_sys_guardrail.server.system_service import get_system_status
from ibki_sys_guardrail.server.openai_service import get_chat_history

# 페이지 설정
st.set_page_config(
    page_title="IBKI 개인정보 가드레일 시스템",
    page_icon="🔒",
    layout="wide"
)

# 시스템 상태 및 설정 초기화
system_status = get_system_status()

# 대화 히스토리 초기화
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = get_chat_history()

# 메인 UI
st.title("🔒 IBKI 개인정보 가드레일 시스템")
st.markdown("---")

# 사이드바 - 시스템 상태 및 사용 가이드
display_system_status(system_status)
display_usage_guide()

# 메인 컨텐츠 영역
# 1. 텍스트 입력 섹션
render_text_input_section(system_status["openai_key"], st.session_state["chat_history"])

# 2. 이미지 입력 섹션
render_image_input_section(system_status["openai_key"], st.session_state["chat_history"])

# 3. ChatGPT 대화 섹션
render_chat_section(system_status["openai_key"], st.session_state["chat_history"]) 