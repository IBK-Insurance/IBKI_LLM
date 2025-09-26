"""
ChatGPT 대화 섹션 모듈
- 독립적인 ChatGPT 대화 UI 및 처리 로직
"""

import streamlit as st
import logging
from ibki_sys_guardrail.server.openai_service import ask_chatgpt, add_to_chat_history
from ibki_sys_guardrail.client.ui_components import display_chat_history

def render_chat_section(openai_api_key, chat_history):
    """ChatGPT 대화 섹션 렌더링"""
    st.markdown("---")
    
    # 대화 히스토리 섹션
    st.markdown("""
    <div class="input-section">
        <h3 style="color: #1e40af; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            💬 대화 기록
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 대화 히스토리 표시
    display_chat_history(chat_history)
    
    # 새로운 질문 입력
    st.markdown("""
    <div style="background: #f8fafc; padding: 1rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #3b82f6;">
        <div style="font-weight: bold; color: #1e40af; margin-bottom: 0.5rem;">새로운 질문하기</div>
    </div>
    """, unsafe_allow_html=True)
    
    user_chat_input = st.text_input("ChatGPT에 질문하기 (항상 가능)", key="chatgpt_input_always", placeholder="새로운 질문을 입력하세요...")
    
    if st.button("ChatGPT로 전송", key="chatgpt_send_btn_always", type="primary") and user_chat_input.strip():
        add_to_chat_history(chat_history, "user", user_chat_input.strip())
        st.info("ChatGPT API 호출 준비 중...")
        print("[DEBUG] ChatGPT API 호출 전: ", user_chat_input)
        logging.info(f"[DEBUG] ChatGPT API 호출 전: {user_chat_input}")
        
        with st.spinner("ChatGPT에 질의 중..."):
            chatgpt_response = ask_chatgpt(user_chat_input.strip(), openai_api_key, history=chat_history)
        
        st.info("ChatGPT API 호출 완료!")
        print("[DEBUG] ChatGPT API 호출 후: ", chatgpt_response)
        logging.info(f"[DEBUG] ChatGPT API 호출 후: {chatgpt_response}")
        
        if chatgpt_response.startswith("OpenAI API 오류:"):
            add_to_chat_history(chat_history, "error", chatgpt_response)
        else:
            add_to_chat_history(chat_history, "assistant", chatgpt_response)
