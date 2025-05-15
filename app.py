from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
import os
from dotenv import load_dotenv
import json
from langchain_qa import InsuranceQASystem

load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# QA 시스템 초기화
qa_system = InsuranceQASystem()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def generate_stream(session_id: str, prompt: str):
    try:
        async for token in qa_system.get_streaming_answer(prompt, session_id=session_id):
            yield f"data: {json.dumps({'token': token})}\n\n"
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