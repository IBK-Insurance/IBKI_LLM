from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
import requests
import os
from dotenv import load_dotenv
from typing import List, Dict
import json
import asyncio
import aiohttp

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
 
필수입력 사항이 없는경우 사용자 입력을 반드시 요구하고 선택입력 사항이 없는경우 기본값으로 아래와 같은 형태로 답변해줘

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
 
* 상품목록
 IBK프리미엄 연금보험 : 비과세, 예금자 보호
 IBK하이브리드연금저축 : 세액공제, 예금자보호, 연말정산
 IBK연금액 평생보증받는 변액연금 : 펀드, 채권 운용, 증권
 
* 필수입력 사항  
 성별
 나이
 
* 선택입력 사항 
 상품명(기본값 : IBK프리미엄 연금보험)
 월보험료(기본값 : 30만원)
 연금개시나이(기본값 : 80세)
 납입기간(기본값 : 10년)
 보증기간(기본값 : 100세)
 보험료 할인방법(기본값 : 보험료 할인)

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

async def generate_stream(session_id: str, prompt: str):
    try:
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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                OLLAMA_API_URL,
                json={
                    "model": "gemma3",
                    "prompt": full_prompt,
                    "stream": True
                }
            ) as response:
                full_response = ""
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line)
                            token = data.get("response", "")
                            full_response += token
                            yield f"data: {json.dumps({'token': token})}\n\n"
                        except json.JSONDecodeError:
                            continue
                
                # 전체 응답을 대화 기록에 추가
                conversations[session_id].append({"role": "assistant", "content": full_response})
                
                # 대화 기록이 너무 길어지면 최근 10개만 유지
                if len(conversations[session_id]) > 20:
                    conversations[session_id] = conversations[session_id][-20:]
                
                yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.post("/generate")
async def generate_response(request: Request, prompt: str = Form(...)):
    session_id = request.cookies.get("session_id", "default")
    return StreamingResponse(
        generate_stream(session_id, prompt),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 