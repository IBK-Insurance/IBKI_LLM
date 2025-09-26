import streamlit as st
import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path so absolute package imports work under Streamlit
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Client 모듈 import
from ibki_sys_guardrail.client.text_input_section import render_text_input_section
from ibki_sys_guardrail.client.image_input_section import render_image_input_section
from ibki_sys_guardrail.client.chat_section import render_chat_section
from ibki_sys_guardrail.client.ui_components import display_system_status

# Server 모듈 import
from ibki_sys_guardrail.server.system_service import get_system_status
from ibki_sys_guardrail.server.openai_service import get_chat_history

# 페이지 설정
st.set_page_config(
    page_title="IBKI AI 가드레일",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일 적용
st.markdown("""
<style>
    /* 메인 컨테이너 스타일 */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* 사이드바 스타일 */
    .sidebar-content {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .mascot-welcome {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 2px solid #f59e0b;
    }
    
    .nav-tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .nav-tab {
        padding: 0.5rem 1rem;
        background: #e5e7eb;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        flex: 1;
    }
    
    .nav-tab.active {
        background: #fbbf24;
        color: #92400e;
        font-weight: bold;
    }
    
    /* 메인 컨텐츠 스타일 */
    .safety-banner {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 4px solid #3b82f6;
    }
    
    .input-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .file-upload-area {
        border: 2px dashed #3b82f6;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8fafc;
        transition: all 0.3s ease;
    }
    
    .file-upload-area:hover {
        background: #e0f2fe;
        border-color: #1e40af;
    }
    
    .main-button {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .main-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    
    /* 채팅 히스토리 스타일 */
    .chat-history {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 10px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .chat-message {
        margin-bottom: 1rem;
        padding: 0.75rem;
        border-radius: 8px;
    }
    
    .chat-user {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .chat-assistant {
        background: #dcfce7;
        color: #166534;
    }
    
    .chat-error {
        background: #fef2f2;
        color: #dc2626;
    }
</style>
""", unsafe_allow_html=True)

# 시스템 상태 및 설정 초기화
system_status = get_system_status()

# 대화 히스토리 초기화
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = get_chat_history()

# 탭 상태 초기화
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "대화기록"

# 메인 헤더
st.markdown("""
<div class="main-header">
    <div class="main-title">
        🛡️ IBKI AI 가드레일
    </div>
    <div class="subtitle">
        귀여운 가드냥이가 지켜주는 안전한 AI 서비스
    </div>
</div>
""", unsafe_allow_html=True)

# 레이아웃 구성
col1, col2 = st.columns([1, 2.5])

with col1:
    # 사이드바 - 가드냥이 마스코트 및 네비게이션
    st.markdown("""
    <div class="sidebar-content">
        <div class="mascot-welcome">
            <div style="font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">🐱</div>
            <div style="text-align: center; font-weight: bold; color: #92400e;">
                안녕하세요! 개인정보를 지켜드리는 AI 가드냥이에요!
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 탭 컨텐츠 구현
    tab1, tab2, tab3 = st.tabs(["📋 대화기록", "📖 사용법", "🔍 판별기준"])
    
    with tab1:
        st.markdown("### 📋 최근 대화 기록")
        
        # 실제 대화 히스토리 표시 (최근 사용자 질의만 노출)
        if st.session_state["chat_history"]:
            user_messages = [m for m in st.session_state["chat_history"] if m.get("role") == "user"]
            recent_user_messages = user_messages[-5:] if user_messages else []

            if recent_user_messages:
                st.markdown('<div class="chat-history">', unsafe_allow_html=True)
                for idx, msg in enumerate(recent_user_messages, start=1):
                    content = msg.get("content", "").strip()
                    preview = (content[:50] + ("..." if len(content) > 50 else "")) if content else "(빈 메시지)"
                    st.markdown(f"""
                    <div class="chat-message chat-user" style="margin-bottom: 0.5rem; padding: 0.5rem; border-radius: 6px;">
                        <div style="font-size: 0.8rem; color: #6b7280; margin-bottom: 0.25rem;">질의 {idx}</div>
                        <div style="font-size: 0.9rem;">{preview}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 1rem; color: #6b7280; background: #f8fafc; 
                            border-radius: 8px; border: 2px dashed #d1d5db;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💬</div>
                    <div>아직 사용자 질의가 없습니다.</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; color: #6b7280; background: #f8fafc; 
                        border-radius: 8px; border: 2px dashed #d1d5db;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💬</div>
                <div>아직 대화 기록이 없습니다.</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📖 사용 방법")
        st.markdown("""
        <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-weight: bold; color: #1e40af; margin-bottom: 0.5rem;">1. 텍스트 입력</div>
            <div style="font-size: 0.9rem; color: #6b7280;">메인 화면에서 텍스트를 직접 입력하여 개인정보 포함 여부를 확인할 수 있습니다.</div>
        </div>
        
        <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-weight: bold; color: #1e40af; margin-bottom: 0.5rem;">2. 이미지 업로드</div>
            <div style="font-size: 0.9rem; color: #6b7280;">이미지 파일(PNG, JPG, JPEG)을 업로드하여 이미지 내 텍스트의 개인정보를 분석합니다.</div>
        </div>
        
        <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-weight: bold; color: #1e40af; margin-bottom: 0.5rem;">3. 개인정보 탐지</div>
            <div style="font-size: 0.9rem; color: #6b7280;">"개인정보 탐지" 버튼을 클릭하거나 이미지 업로드 시 자동으로 분석이 시작됩니다.</div>
        </div>
        
        <div style="background: #f8fafc; padding: 1rem; border-radius: 8px;">
            <div style="font-weight: bold; color: #1e40af; margin-bottom: 0.5rem;">4. AI 연결</div>
            <div style="font-size: 0.9rem; color: #6b7280;">개인정보가 포함되지 않은 경우 자동으로 ChatGPT와 연결됩니다.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🔍 판별 기준")
        st.markdown("""
        <div style="background: #fef2f2; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #dc2626;">
            <div style="font-weight: bold; color: #dc2626; margin-bottom: 0.5rem;">🚨 개인정보로 판별되는 항목</div>
            <div style="font-size: 0.9rem; color: #7f1d1d;">
                • 이름, 주민등록번호, 연락처<br>
                • 이메일 주소, 주소<br>
                • 계좌번호, 신용카드 번호<br>
                • 기타 개인을 식별할 수 있는 정보
            </div>
        </div>
        
        <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #16a34a;">
            <div style="font-weight: bold; color: #16a34a; margin-bottom: 0.5rem;">✅ 개인정보가 아닌 항목</div>
            <div style="font-size: 0.9rem; color: #166534;">
                • 일반적인 직업명 (예: 개발자, 디자이너)<br>
                • 나이대 (예: 20대, 30대)<br>
                • 지역명 (시/도 단위)<br>
                • 일반적인 취미나 관심사
            </div>
        </div>
        
        <div style="background: #fffbeb; padding: 1rem; border-radius: 8px; border-left: 4px solid #f59e0b;">
            <div style="font-weight: bold; color: #f59e0b; margin-bottom: 0.5rem;">⚠️ 주의사항</div>
            <div style="font-size: 0.9rem; color: #92400e;">
                • 이 도구는 참고용이며, 법적 판단의 근거로 사용하지 마세요<br>
                • 실제 개인정보 처리 시에는 관련 법규를 준수하세요
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 시스템 상태 표시
    display_system_status(system_status)

with col2:
    # 메인 컨텐츠 영역
    st.markdown("""
    <div class="safety-banner">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.2rem;">🐾</span>
            <strong>가드냥이가 모든 입력 내용을 꼼꼼히 검사한 후 안전이 확인되면 AI와 연결해드려요!</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 안전 보장 배너
    st.markdown("### 🤖 AI에게 무엇을 물어볼까요?")
    
    # 텍스트 입력 섹션
    render_text_input_section(system_status["openai_key"], st.session_state["chat_history"])
    
    # 이미지 입력 섹션  
    render_image_input_section(system_status["openai_key"], st.session_state["chat_history"])
    
    # ChatGPT 대화 섹션
    render_chat_section(system_status["openai_key"], st.session_state["chat_history"]) 