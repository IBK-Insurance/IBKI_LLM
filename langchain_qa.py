from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import asyncio
import json
from typing import Dict, Optional

class InsuranceQASystem:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gemma3"):
        """
        보험 QA 시스템 초기화
        
        Args:
            base_url (str): Ollama API 기본 URL
            model (str): 사용할 모델 이름
        """
        self.base_url = base_url
        self.model = model
        self.conversation_chains: Dict[str, LLMChain] = {}
        
        # 기본 시스템 프롬프트
        self.default_system_prompt = """당신은 IBK연금보험 전문 상담원입니다.
사용자의 질문에 대해 친절하고 정확하게 답변해주세요.

답변 시 다음 사항을 반드시 포함해주세요:
1. 상품의 주요 특징
2. 가입 조건 및 제한사항
3. 보험료 관련 정보
4. 연금 수령 관련 정보
5. 세제 혜택 정보

답변은 한국어로 작성하며, 필요한 경우 숫자나 전문 용어는 괄호 안에 영어로 함께 표기해주세요."""

    def get_or_create_chain(self, session_id: str, system_prompt: Optional[str] = None) -> LLMChain:
        """
        세션 ID에 해당하는 LangChain 체인을 가져오거나 생성
        
        Args:
            session_id (str): 세션 ID
            system_prompt (str, optional): 사용자 정의 시스템 프롬프트
            
        Returns:
            LLMChain: LangChain 체인
        """
        if session_id not in self.conversation_chains:
            # Ollama 모델 초기화
            llm = Ollama(
                base_url=self.base_url,
                model=self.model,
                callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
            )

            # 프롬프트 템플릿 설정
            prompt_template = PromptTemplate(
                input_variables=["context", "prompt"],
                template=f"""{system_prompt or self.default_system_prompt}

이전 대화 내용:
{{context}}

현재 사용자 메시지: {{prompt}}"""
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
            
            self.conversation_chains[session_id] = chain
        
        return self.conversation_chains[session_id]

    async def get_answer(self, 
                        question: str, 
                        session_id: str = "default",
                        system_prompt: Optional[str] = None) -> str:
        """
        질문에 대한 답변 생성
        
        Args:
            question (str): 사용자 질문
            session_id (str): 세션 ID
            system_prompt (str, optional): 사용자 정의 시스템 프롬프트
            
        Returns:
            str: 생성된 답변
        """
        chain = self.get_or_create_chain(session_id, system_prompt)
        response = await chain.arun(prompt=question)
        return response

    async def get_streaming_answer(self, 
                                 question: str, 
                                 session_id: str = "default",
                                 system_prompt: Optional[str] = None):
        """
        스트리밍 방식으로 질문에 대한 답변 생성
        
        Args:
            question (str): 사용자 질문
            session_id (str): 세션 ID
            system_prompt (str, optional): 사용자 정의 시스템 프롬프트
            
        Yields:
            str: 생성된 답변의 토큰
        """
        chain = self.get_or_create_chain(session_id, system_prompt)
        
        # 스트리밍을 위한 큐 생성
        queue = asyncio.Queue()
        
        # 콜백 핸들러 설정
        class StreamingCallbackHandler(StreamingStdOutCallbackHandler):
            def __init__(self, queue):
                super().__init__()
                self.queue = queue

            async def on_llm_new_token(self, token: str, **kwargs) -> None:
                await self.queue.put(token)
        
        callback_handler = StreamingCallbackHandler(queue)
        chain.llm.callback_manager = CallbackManager([callback_handler])
        
        # 비동기로 응답 생성
        async def generate():
            await chain.arun(prompt=question)
            await queue.put(None)  # 스트리밍 종료 신호
        
        # 백그라운드에서 응답 생성 시작
        asyncio.create_task(generate())
        
        # 스트리밍 응답 생성
        while True:
            token = await queue.get()
            if token is None:
                break
            yield token

# 사용 예시
async def main():
    # QA 시스템 초기화
    qa_system = InsuranceQASystem()
    
    # 일반 질문 예시
    question = "IBK프리미엄 연금보험의 특징과 장점을 알려주세요."
    answer = await qa_system.get_answer(question)
    print(f"질문: {question}")
    print(f"답변: {answer}\n")
    
    # 스트리밍 방식 예시
    question2 = "연금 수령 시 세제 혜택은 어떻게 되나요?"
    print(f"질문: {question2}")
    print("답변: ", end="")
    async for token in qa_system.get_streaming_answer(question2):
        print(token, end="", flush=True)
    print("\n")
    
    # 사용자 정의 시스템 프롬프트 예시
    custom_prompt = """당신은 IBK연금보험의 세제 전문가입니다.
세제 관련 질문에 대해 상세히 답변해주세요.
답변 시 다음 사항을 반드시 포함해주세요:
1. 세제 혜택의 종류
2. 세제 혜택의 조건
3. 세제 혜택의 한도
4. 세제 혜택의 신청 방법"""
    
    question3 = "연금보험의 세제 혜택에 대해 알려주세요."
    answer = await qa_system.get_answer(question3, system_prompt=custom_prompt)
    print(f"질문: {question3}")
    print(f"답변: {answer}")

if __name__ == "__main__":
    asyncio.run(main()) 