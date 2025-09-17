"""
UI 컴포넌트 모듈
- 재사용 가능한 UI 컴포넌트들
- 결과 표시 컴포넌트
"""

import streamlit as st

def display_personal_info_result(result, result_type="텍스트"):
    """개인정보 판별 결과 표시"""
    if "포함됨" in result:
        st.error("🚨 개인정보가 포함되어 있습니다!")
        st.markdown("**결과:** 포함됨")
        details = result.replace("포함됨", "").strip()
        if details:
            with st.expander("🔎 포함된 개인정보 내용 보기", expanded=True):
                st.text_area("포함된 개인정보", details, height=150, disabled=True)
    elif "포함되지 않음" in result:
        st.success("✅ 개인정보가 포함되어 있지 않습니다!")
        st.markdown("**결과:** 포함되지 않음")
    else:
        st.warning("⚠️ 판별 결과를 확인할 수 없습니다.")
    st.markdown(f"**결과:** {result}")

def display_chatgpt_response(chatgpt_response, response_type="분석 결과"):
    """ChatGPT 응답 표시"""
    if chatgpt_response and not chatgpt_response.startswith("OpenAI API 오류:"):
        with st.expander(f"💬 ChatGPT 응답 ({response_type})", expanded=True):
            st.text_area("ChatGPT 응답", chatgpt_response, height=200, disabled=True)
    elif chatgpt_response and chatgpt_response.startswith("OpenAI API 오류:"):
        st.error(f"ChatGPT API 오류: {chatgpt_response}")

def display_chat_history(chat_history):
    """대화 히스토리 표시"""
    i = 0
    while i < len(chat_history):
        msg = chat_history[i]
        if msg["role"] == "user":
            st.markdown(
                f"<div style='background:#e6f7ff;padding:8px;border-radius:6px;margin-bottom:4px;color:#0050b3'><b>🙋 사용자:</b><br>{msg['content']}</div>",
                unsafe_allow_html=True
            )
            if i + 1 < len(chat_history) and chat_history[i + 1]["role"] in ("assistant", "error"):
                next_msg = chat_history[i + 1]
                if next_msg["role"] == "assistant":
                    st.markdown(
                        f"<div style='background:#f6ffed;padding:8px;border-radius:6px;margin-bottom:12px;color:#237804'><b>🤖 ChatGPT:</b><br>{next_msg['content']}</div>",
                        unsafe_allow_html=True
                    )
                elif next_msg["role"] == "error":
                    st.markdown(
                        f"<div style='background:#fff1f0;padding:8px;border-radius:6px;margin-bottom:12px;color:#a8071a'><b>❌ 오류:</b><br>{next_msg['content']}</div>",
                        unsafe_allow_html=True
                    )
                i += 2
            else:
                i += 1
        else:
            if msg["role"] == "assistant":
                st.markdown(
                    f"<div style='background:#f6ffed;padding:8px;border-radius:6px;margin-bottom:12px;color:#237804'><b>🤖 ChatGPT:</b><br>{msg['content']}</div>",
                    unsafe_allow_html=True
                )
            elif msg["role"] == "error":
                st.markdown(
                    f"<div style='background:#fff1f0;padding:8px;border-radius:6px;margin-bottom:12px;color:#a8071a'><b>❌ 오류:</b><br>{msg['content']}</div>",
                    unsafe_allow_html=True
                )
            i += 1

def display_system_status(system_status):
    """시스템 상태 표시"""
    with st.sidebar:
        st.markdown("---")
        st.header("⚙️ 시스템 상태")
        
        # Ollama 연결 상태
        if system_status["ollama_connected"]:
            st.success(system_status["ollama_message"])
        else:
            st.error(system_status["ollama_message"])
            st.info("Ollama 서버가 실행 중인지 확인하세요")

def display_usage_guide():
    """사용 방법 가이드 표시"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("""
        ### 📋 사용 방법
        1. **텍스트 입력**: 메인 화면에서 텍스트를 직접 입력
        2. **이미지 업로드**: 메인 화면에서 이미지 파일(PNG, JPG, JPEG) 업로드
        3. **개인정보 탐지**: "개인정보 탐지" 버튼 클릭 또는 이미지 업로드 시 자동 분석

        ### 🔍 판별 기준
        - **개인정보**: 이름, 주민등록번호, 연락처, 이메일, 주소, 계좌번호 등
        - **개인정보 아님**: 일반적인 직업명, 나이대, 지역명(시/도 단위) 등

        ### ⚠️ 주의사항
        - 이 도구는 참고용이며, 법적 판단의 근거로 사용하지 마세요
        - 실제 개인정보 처리 시에는 관련 법규를 준수하세요
        """)
