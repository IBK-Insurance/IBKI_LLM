"""
이미지 입력 섹션 모듈
- 이미지 업로드 UI 및 처리 로직
"""

import streamlit as st
import logging
from ibki_sys_guardrail.server.llm_service import check_personal_info_image, extract_text_from_image_llm
from ibki_sys_guardrail.server.openai_service import ask_chatgpt, add_to_chat_history
from ibki_sys_guardrail.client.ui_components import display_personal_info_result, display_chatgpt_response

def render_image_input_section(openai_api_key, chat_history):
    """이미지 입력 섹션 렌더링"""
    st.markdown("""
    <div class="input-section">
        <h3 style="color: #1e40af; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            🖼️ 파일도 함께 올려보세요! (선택사항)
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 파일 업로드 영역 스타일링
    st.markdown("""
    <div class="file-upload-area">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
        <div style="font-weight: bold; color: #1e40af; margin-bottom: 0.5rem;">
            파일을 여기로 끌어다 놓거나 클릭해주세요!
        </div>
        <div style="color: #6b7280; font-size: 0.9rem;">
            PDF, Word, Excel, 이미지 파일을 지원해요 🐾
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_image_file = st.file_uploader(
        "이미지 파일을 선택하세요",
        type=["png", "jpg", "jpeg"],
        key="independent_image_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_image_file is not None:
        from PIL import Image
        user_image = Image.open(uploaded_image_file)
        st.image(user_image, caption="업로드 이미지", use_container_width=True)
        
        # 이미지에서 텍스트 추출
        with st.spinner("이미지에서 텍스트 추출 중..."):
            image_extracted_text = extract_text_from_image_llm(user_image)
        
        if image_extracted_text:
            with st.expander("🖼️ 이미지에서 추출된 텍스트 미리보기", expanded=False):
                st.text_area("이미지 추출 텍스트", image_extracted_text, height=200, disabled=True, key="image_extracted_text_area_preview")
        
        # 대화 기록에 사용자 질의 즉시 반영 (이미지에서 추출된 텍스트)
        if image_extracted_text:
            if not chat_history or chat_history[-1].get("role") != "user" or chat_history[-1].get("content") != image_extracted_text:
                add_to_chat_history(chat_history, "user", image_extracted_text)

        # 이미지에서 개인정보 판별
        with st.spinner("이미지에서 텍스트 추출 및 분석 중..."):
            image_result = check_personal_info_image(user_image)
        
        # 개인정보 판별 결과 표시
        display_personal_info_result(image_result, "이미지")
        
        # 개인정보가 포함되지 않은 경우 ChatGPT API 자동 호출
        if "포함되지 않음" in image_result:
            chatgpt_response = None
            if openai_api_key and image_extracted_text:
                add_to_chat_history(chat_history, "user", image_extracted_text)
                st.info("ChatGPT API 호출 준비 중...")
                print("[DEBUG] ChatGPT API 호출 전: ", image_extracted_text)
                logging.info(f"[DEBUG] ChatGPT API 호출 전: {image_extracted_text}")
                with st.spinner("ChatGPT에 질의 중..."):
                    chatgpt_response = ask_chatgpt(image_extracted_text, openai_api_key, history=chat_history)
                st.info("ChatGPT API 호출 완료!")
                print("[DEBUG] ChatGPT API 호출 후: ", chatgpt_response)
                logging.info(f"[DEBUG] ChatGPT API 호출 후: {chatgpt_response}")
                
                if chatgpt_response.startswith("OpenAI API 오류:"):
                    add_to_chat_history(chat_history, "error", chatgpt_response)
                else:
                    add_to_chat_history(chat_history, "assistant", chatgpt_response)
                
                # ChatGPT 응답 표시
                display_chatgpt_response(chatgpt_response, "분석 결과")
            elif not openai_api_key:
                st.warning("환경설정 파일(.env)에 OPENAI_API_KEY가 설정되어 있지 않습니다.")

        # 사이드바 대화기록 탭 갱신을 위해 다시 렌더링
        st.rerun()
