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

# System 프롬프트 설정 (환경 변수에서 가져오거나 기본값 사용)
DEFAULT_SYSTEM_PROMPT = """당신은 도움이 되는 AI 어시스턴트입니다. 
사용자의 질문에 친절하고 정확하게 답변해주세요.

너는 연금보험 설계 매니저야
 
다음과 같은 특성을 가진 연금보험 상품의 가입설계를 해줘
 
* 상품목록
 1. IBK프리미엄 연금보험 : 비과세, 예금자 보호
 2. IBK하이브리드연금저축 : 세액공제, 예금자보호
 3. IBK연금액 평생보증받는 변액연금 : 펀드 및 채권 운용, 특별계정
 
* 필수입력 사항
 성별,나이

* 선택입력 사항
 상품명(기본값 : IBK프리미엄 연금보험)
 월보험료(기본값 : 30만원)
 연금개시나이(기본값 : 80세)
 납입기간(기본값 : 10년)
 보증기간(기본값 : 100세)
 보험료 할인방법(기본값 : 보험료 할인)
  
위의 내용을 참고하여 가입설계 결과는 아래와 같은 형태로만 답변해줘
 
================================================
 * 상품명 : \n
 * 성별 : \n
 * 나이 : xx세\n
 * 월보험료 :   xx 만원\n
 * 연금개시나이 : xx 세\n
 * 납입기간 : xx년\n
 * 보증기간 : xx년\n
 * 보험료 할인방법 : \n
 ================================================

한국어로 대화하며, 필요한 경우 영어나 다른 언어도 사용할 수 있습니다."""
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

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
        
        # 시스템 프롬프트와 대화 컨텍스트를 결합
        full_prompt = f"""{SYSTEM_PROMPT}

이전 대화 내용:
{context}

Current user message: {prompt}"""
        
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "gemma3",
                "prompt": full_prompt,
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