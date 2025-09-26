"""
UI 컴포넌트 모듈
- 재사용 가능한 UI 컴포넌트들
- 결과 표시 컴포넌트
"""

import streamlit as st

def display_personal_info_result(result, result_type="텍스트"):
    """개인정보 판별 결과 표시"""
    if "포함됨" in result:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); 
                    padding: 1rem; border-radius: 10px; border-left: 4px solid #dc2626; 
                    margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem;">🚨</span>
                <strong style="color: #dc2626; font-size: 1.1rem;">개인정보가 포함되어 있습니다!</strong>
            </div>
            <div style="color: #7f1d1d; font-weight: bold;">결과: 포함됨</div>
        </div>
        """, unsafe_allow_html=True)
        
        details = result.replace("포함됨", "").strip()
        if details:
            with st.expander("🔎 포함된 개인정보 내용 보기", expanded=True):
                st.text_area("포함된 개인정보", details, height=150, disabled=True)
    elif "포함되지 않음" in result:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); 
                    padding: 1rem; border-radius: 10px; border-left: 4px solid #16a34a; 
                    margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem;">✅</span>
                <strong style="color: #16a34a; font-size: 1.1rem;">개인정보가 포함되어 있지 않습니다!</strong>
            </div>
            <div style="color: #166534; font-weight: bold;">결과: 포함되지 않음</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); 
                    padding: 1rem; border-radius: 10px; border-left: 4px solid #f59e0b; 
                    margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem;">⚠️</span>
                <strong style="color: #f59e0b; font-size: 1.1rem;">판별 결과를 확인할 수 없습니다.</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_chatgpt_response(chatgpt_response, response_type="분석 결과"):
    """ChatGPT 응답 표시"""
    if chatgpt_response and not chatgpt_response.startswith("OpenAI API 오류:"):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                    padding: 1rem; border-radius: 10px; border-left: 4px solid #0ea5e9; 
                    margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem;">💬</span>
                <strong style="color: #0c4a6e; font-size: 1.1rem;">ChatGPT 응답 ({})</strong>
            </div>
        </div>
        """.format(response_type), unsafe_allow_html=True)
        
        with st.expander("📝 상세 응답 보기", expanded=True):
            st.text_area("ChatGPT 응답", chatgpt_response, height=200, disabled=True)
    elif chatgpt_response and chatgpt_response.startswith("OpenAI API 오류:"):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); 
                    padding: 1rem; border-radius: 10px; border-left: 4px solid #dc2626; 
                    margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem;">❌</span>
                <strong style="color: #dc2626; font-size: 1.1rem;">ChatGPT API 오류</strong>
            </div>
            <div style="color: #7f1d1d;">{}</div>
        </div>
        """.format(chatgpt_response), unsafe_allow_html=True)

def display_chat_history(chat_history):
    """대화 히스토리 표시"""
    if not chat_history:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #6b7280; background: #f8fafc; 
                    border-radius: 10px; border: 2px dashed #d1d5db;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
            <div>아직 대화 기록이 없습니다.</div>
            <div style="font-size: 0.9rem; margin-top: 0.5rem;">AI와 대화를 시작해보세요!</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    
    i = 0
    while i < len(chat_history):
        msg = chat_history[i]
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="chat-message chat-user">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.2rem;">🙋</span>
                        <strong>사용자</strong>
                    </div>
                    <div>{msg['content']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if i + 1 < len(chat_history) and chat_history[i + 1]["role"] in ("assistant", "error"):
                next_msg = chat_history[i + 1]
                if next_msg["role"] == "assistant":
                    st.markdown(
                        f"""
                        <div class="chat-message chat-assistant">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                <span style="font-size: 1.2rem;">🤖</span>
                                <strong>ChatGPT</strong>
                            </div>
                            <div>{next_msg['content']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                elif next_msg["role"] == "error":
                    st.markdown(
                        f"""
                        <div class="chat-message chat-error">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                <span style="font-size: 1.2rem;">❌</span>
                                <strong>오류</strong>
                            </div>
                            <div>{next_msg['content']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                i += 2
            else:
                i += 1
        else:
            if msg["role"] == "assistant":
                st.markdown(
                    f"""
                    <div class="chat-message chat-assistant">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2rem;">🤖</span>
                            <strong>ChatGPT</strong>
                        </div>
                        <div>{msg['content']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif msg["role"] == "error":
                st.markdown(
                    f"""
                    <div class="chat-message chat-error">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2rem;">❌</span>
                            <strong>오류</strong>
                        </div>
                        <div>{msg['content']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            i += 1
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_system_status(system_status):
    """시스템 상태 표시"""
    st.markdown("---")
    st.markdown("### ⚙️ 시스템 상태")
    
    # Ollama 연결 상태
    if system_status["ollama_connected"]:
        st.markdown("""
        <div style="background: #f0fdf4; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #16a34a; margin-bottom: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="color: #16a34a;">✅</span>
                <span style="color: #166534; font-weight: bold;">{}</span>
            </div>
        </div>
        """.format(system_status["ollama_message"]), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: #fef2f2; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #dc2626; margin-bottom: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="color: #dc2626;">❌</span>
                <span style="color: #7f1d1d; font-weight: bold;">{}</span>
            </div>
        </div>
        """.format(system_status["ollama_message"]), unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #f0f9ff; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #0ea5e9;">
            <div style="color: #0c4a6e; font-size: 0.9rem;">
                💡 Ollama 서버가 실행 중인지 확인하세요
            </div>
        </div>
        """, unsafe_allow_html=True)

