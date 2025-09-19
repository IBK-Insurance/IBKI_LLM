"""
OpenAI 서비스 모듈
- ChatGPT API 호출 및 관리
- 대화 히스토리 관리
"""

import logging
import os
from typing import List, Dict, Optional

from pathlib import Path
from dotenv import load_dotenv
try:
    from openai import OpenAI  # >=1.0 style
except Exception:
    OpenAI = None  # fallback for older openai


def _resolve_openai_key(explicit_key: Optional[str]) -> Optional[str]:
    """명시 키가 없으면 .env를 로드하여 OPENAI_API_KEY를 반환."""
    if explicit_key:
        return explicit_key
    # Load .env from ibki_sys_guardrail/.env explicitly
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path)
    return os.getenv("OPENAI_API_KEY")


def ask_chatgpt(query: str, openai_api_key: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> str:
    """ChatGPT API 호출 (.env의 OPENAI_API_KEY 지원)."""
    print("[DEBUG] ask_chatgpt 진입, query:", query)
    try:
        # 키 해석
        api_key = _resolve_openai_key(openai_api_key)
        if not api_key:
            return "OpenAI API 오류: OPENAI_API_KEY가 설정되지 않았습니다 (.env 확인)."

        # 대화 히스토리 준비
        messages: List[Dict[str, str]] = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": query})

        # 최신 OpenAI 클라이언트 사용 (>=1.0). 없으면 구버전 방식으로 폴백
        if OpenAI is not None:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            print("[DEBUG] ask_chatgpt 응답:", response)
            return response.choices[0].message.content or ""
        else:
            import openai  # type: ignore
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            print("[DEBUG] ask_chatgpt 응답:", response)
            return response["choices"][0]["message"]["content"]
    except Exception as e:
        print("[DEBUG] ask_chatgpt 오류:", str(e))
        return f"OpenAI API 오류: {str(e)}"


def add_to_chat_history(chat_history: List[Dict[str, str]], role: str, content: str) -> List[Dict[str, str]]:
    """대화 히스토리에 메시지 추가"""
    chat_history.append({"role": role, "content": content})
    return chat_history


def get_chat_history() -> List[Dict[str, str]]:
    """대화 히스토리 반환 (빈 리스트로 초기화)"""
    return []
