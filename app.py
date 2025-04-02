from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import requests
import os
from dotenv import load_dotenv
from typing import List, Dict
import json

load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# 대화 기록을 저장할 딕셔너리
conversations: Dict[str, List[Dict[str, str]]] = {}

def get_conversation_history(session_id: str) -> str:
    """대화 기록을 문자열로 변환"""
    if session_id not in conversations:
        return ""
    
    history = ""
    for msg in conversations[session_id]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"
    return history

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate_response(request: Request, prompt: str = Form(...)):
    try:
        # 세션 ID 가져오기 (쿠키에서)
        session_id = request.cookies.get("session_id", "default")
        
        # 대화 기록이 없으면 초기화
        if session_id not in conversations:
            conversations[session_id] = []
        
        # 사용자 메시지 추가
        conversations[session_id].append({"role": "user", "content": prompt})
        
        # 전체 대화 컨텍스트 생성
        context = get_conversation_history(session_id)
        
        # 시스템 프롬프트 추가
        system_prompt = """당신은 도움이 되는 AI 어시스턴트입니다. 이전 대화 내용을 바탕으로 대화를 이어가주세요.
이전 대화 내용:
{context}

Current user message: {prompt}""".format(context=context, prompt=prompt)
        
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "gemma3",
                "prompt": system_prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        
        # 응답 가져오기
        assistant_response = response.json()["response"]
        
        # 어시스턴트 응답을 대화 기록에 추가
        conversations[session_id].append({"role": "assistant", "content": assistant_response})
        
        # 대화 기록이 너무 길어지면 최근 10개만 유지
        if len(conversations[session_id]) > 20:  # 10개의 대화 쌍
            conversations[session_id] = conversations[session_id][-20:]
        
        return {"response": assistant_response}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 