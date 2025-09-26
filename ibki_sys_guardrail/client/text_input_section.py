"""
텍스트 입력 섹션 모듈
- 텍스트 입력 UI 및 처리 로직
"""

import streamlit as st
import logging
from ibki_sys_guardrail.server.llm_service import check_personal_info
from ibki_sys_guardrail.server.openai_service import ask_chatgpt, add_to_chat_history
from ibki_sys_guardrail.client.ui_components import display_personal_info_result, display_chatgpt_response

def render_text_input_section(openai_api_key, chat_history):
    """텍스트 입력 섹션 렌더링"""
    st.markdown("""
    <div class="input-section">
        <h3 style="color: #1e40af; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            📄 텍스트 입력
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 예시 질문들 표시
    st.markdown("""
    <div style="background: #f8fafc; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #3b82f6;">
        <div style="font-weight: bold; color: #1e40af; margin-bottom: 0.5rem;">💡 예시 질문</div>
        <div style="color: #6b7280; font-size: 0.9rem;">
            • 업무 효율성을 높이는 방법은?<br>
            • 창의적인 마케팅 아이디어 주세요
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    user_text = st.text_area(
        "안녕하세요! 궁금한 것을 자유롭게 물어보세요 😺",
        height=200,
        placeholder="개인정보 포함여부를 확인할 텍스트를 입력하세요...",
        key="independent_text_input"
    )

    # 개인정보 탐지 버튼
    개인정보탐지 = st.button(
        "개인정보탐지", 
        key="submit_text_input", 
        disabled=not (user_text and user_text.strip()),
        type="primary"
    )

    # '개인정보 탐지' 버튼을 눌렀을 때만 개인정보 판별 로직 실행
    if 개인정보탐지 and user_text and user_text.strip():
        # 대화 기록에 사용자 질의 즉시 반영 (중복 방지)
        if not chat_history or chat_history[-1].get("role") != "user" or chat_history[-1].get("content") != user_text.strip():
            add_to_chat_history(chat_history, "user", user_text.strip())

        with st.spinner("분석 중..."):
            text_result = check_personal_info(user_text.strip())
        
        # 개인정보 판별 결과 표시
        display_personal_info_result(text_result, "텍스트")
        
        # 개인정보가 포함되지 않은 경우 ChatGPT API 자동 호출
        if "포함되지 않음" in text_result:
            chatgpt_response = None
            if openai_api_key:
                st.info("ChatGPT API 호출 준비 중...")
                print("[DEBUG] ChatGPT API 호출 전: ", user_text.strip())
                logging.info(f"[DEBUG] ChatGPT API 호출 전: {user_text.strip()}")
                with st.spinner("ChatGPT에 질의 중..."):
                    chatgpt_response = ask_chatgpt(user_text.strip(), openai_api_key, history=chat_history)
                st.info("ChatGPT API 호출 완료!")
                print("[DEBUG] ChatGPT API 호출 후: ", chatgpt_response)
                logging.info(f"[DEBUG] ChatGPT API 호출 후: {chatgpt_response}")
                
                if chatgpt_response.startswith("OpenAI API 오류:"):
                    add_to_chat_history(chat_history, "error", chatgpt_response)
                else:
                    add_to_chat_history(chat_history, "assistant", chatgpt_response)
                
                # ChatGPT 응답 표시
                display_chatgpt_response(chatgpt_response, "분석 결과")
            else:
                st.warning("환경설정 파일(.env)에 OPENAI_API_KEY가 설정되어 있지 않습니다.")

        # 사이드바 대화기록 탭 갱신을 위해 다시 렌더링
        st.rerun()
