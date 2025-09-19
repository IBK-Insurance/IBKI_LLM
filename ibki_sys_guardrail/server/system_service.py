"""
시스템 서비스 모듈
- 시스템 상태 확인
- 환경 설정 관리
"""

import streamlit as st
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """환경설정 파일(ibki_sys_guardrail/.env)에서 API 키 로드"""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path)
    return os.getenv("OPENAI_API_KEY")

def check_ollama_connection():
    """Ollama 서버 연결 상태 확인"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return True, "✅ Ollama 서버 연결됨"
        else:
            return False, "❌ Ollama 서버 연결 실패"
    except:
        return False, "❌ Ollama 서버 연결 실패"

def get_system_status():
    """시스템 상태 정보 반환"""
    ollama_connected, ollama_message = check_ollama_connection()
    openai_key = load_environment()
    
    return {
        "ollama_connected": ollama_connected,
        "ollama_message": ollama_message,
        "openai_key_available": bool(openai_key),
        "openai_key": openai_key
    }
