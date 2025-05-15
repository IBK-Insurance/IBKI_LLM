import requests
import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming import StreamingStdOutCallbackHandler

# 환경 변수 로드
load_dotenv()

class Message(BaseModel):
    """대화 메시지 모델"""
    role: str
    content: str

class Conversation(BaseModel):
    """대화 기록 모델"""
    messages: List[Message] = Field(default_factory=list)
    
    def add_message(self, role: str, content: str) -> None:
        """대화에 메시지 추가"""
        self.messages.append(Message(role=role, content=content))
    
    def get_history(self) -> str:
        """대화 기록을 문자열로 변환"""
        history = ""
        for msg in self.messages:
            role = "사용자" if msg.role == "user" else "어시스턴트"
            history += f"{role}: {msg.content}\n"
        return history
    
    def truncate(self, max_messages: int = 20) -> None:
        """대화 기록이 너무 길어지면 최근 메시지만 유지"""
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]

class OllamaClient:
    """Ollama API 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.conversations: Dict[str, Conversation] = {}
        self.callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        
    def _get_conversation(self, session_id: str) -> Conversation:
        """세션 ID에 해당하는 대화 기록 가져오기"""
        if session_id not in self.conversations:
            self.conversations[session_id] = Conversation()
        return self.conversations[session_id]
    
    def generate(self, 
                prompt: str, 
                model: str = "gemma3", 
                session_id: str = "default",
                system_prompt: Optional[str] = None) -> str:
        """
        Ollama API를 통해 응답 생성
        
        Args:
            prompt: 사용자 입력 프롬프트
            model: 사용할 모델 이름
            session_id: 대화 세션 ID
            system_prompt: 시스템 프롬프트 (기본값: None)
            
        Returns:
            생성된 응답 텍스트
        """
        # 대화 기록 가져오기
        conversation = self._get_conversation(session_id)
        
        # 사용자 메시지 추가
        conversation.add_message("user", prompt)
        
        # 전체 대화 컨텍스트 생성
        context = conversation.get_history()
        
        # 기본 시스템 프롬프트 설정
        if system_prompt is None:
            system_prompt = """당신은 도움이 되는 AI 어시스턴트입니다. 이전 대화 내용을 바탕으로 대화를 이어가주세요.
이전 대화 내용:
{context}

현재 사용자 메시지: {prompt}"""

        # LangChain Ollama 모델 초기화
        llm = Ollama(
            base_url=self.base_url,
            model=model,
            callback_manager=self.callback_manager
        )

        # 프롬프트 템플릿 설정
        prompt_template = PromptTemplate(
            input_variables=["context", "prompt"],
            template=system_prompt
        )

        # 대화 메모리 설정
        memory = ConversationBufferMemory(
            memory_key="context",
            return_messages=True
        )

        # LangChain 체인 생성
        chain = LLMChain(
            llm=llm,
            prompt=prompt_template,
            memory=memory
        )

        # 응답 생성
        response = chain.run(context=context, prompt=prompt)
        
        # 어시스턴트 응답을 대화 기록에 추가
        conversation.add_message("assistant", response)
        
        # 대화 기록이 너무 길어지면 최근 메시지만 유지
        conversation.truncate()
        
        return response
    
    def list_models(self) -> List[Dict[str, Any]]:
        """사용 가능한 모델 목록 가져오기"""
        response = requests.get(f"{self.base_url}/api/tags")
        response.raise_for_status()
        return response.json()["models"]
    
    def pull_model(self, model_name: str) -> Dict[str, Any]:
        """모델 다운로드"""
        response = requests.post(
            f"{self.base_url}/api/pull",
            json={"name": model_name}
        )
        response.raise_for_status()
        return response.json()
    
    def delete_model(self, model_name: str) -> Dict[str, Any]:
        """모델 삭제"""
        response = requests.delete(
            f"{self.base_url}/api/delete",
            json={"name": model_name}
        )
        response.raise_for_status()
        return response.json() 