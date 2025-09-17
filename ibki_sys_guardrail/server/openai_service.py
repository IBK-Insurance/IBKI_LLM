"""
OpenAI 서비스 모듈
- ChatGPT API 호출 및 관리
- 대화 히스토리 관리
"""

import openai
import logging

def ask_chatgpt(query, openai_api_key, history=None):
    """ChatGPT API 호출"""
    print("[DEBUG] ask_chatgpt 진입, query:", query)
    try:
        # 대화 히스토리 준비
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": query})
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            api_key=openai_api_key,
            max_tokens=1024,
            temperature=0.7,
        )
        print("[DEBUG] ask_chatgpt 응답:", response)
        return response.choices[0].message.content
    except Exception as e:
        print("[DEBUG] ask_chatgpt 오류:", str(e))
        return f"OpenAI API 오류: {str(e)}"

def add_to_chat_history(chat_history, role, content):
    """대화 히스토리에 메시지 추가"""
    chat_history.append({"role": role, "content": content})
    return chat_history

def get_chat_history():
    """대화 히스토리 반환 (빈 리스트로 초기화)"""
    return []
