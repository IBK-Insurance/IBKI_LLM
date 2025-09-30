"""
RAG (Retrieval-Augmented Generation) 서비스 모듈
- 개인정보 판별을 위한 상세정보 저장 및 검색
- VectorDB를 활용한 지식베이스 구축
- LLM과 연동한 개인정보 탐지 정확도 향상
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib

# VectorDB 및 임베딩 관련 라이브러리
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    print("필요한 라이브러리를 설치해주세요: pip install chromadb sentence-transformers")
    raise

from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PIIKnowledgeBase:
    """개인정보 탐지를 위한 지식베이스 클래스"""
    
    def __init__(self, persist_directory: str = "./vectordb", model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        RAG 서비스 초기화
        
        Args:
            persist_directory: VectorDB 저장 디렉토리
            model_name: 임베딩 모델명
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # ChromaDB 클라이언트 초기화
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 컬렉션 초기화
        self.collection_name = "pii_detection_knowledge"
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            logger.info(f"기존 컬렉션 '{self.collection_name}' 로드됨")
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "개인정보 탐지를 위한 지식베이스"}
            )
            logger.info(f"새 컬렉션 '{self.collection_name}' 생성됨")
        
        # 임베딩 모델 초기화
        self.embedding_model = SentenceTransformer(model_name)
        logger.info(f"임베딩 모델 '{model_name}' 로드됨")
        
        # 개인정보 탐지 패턴 및 예시 데이터 초기화
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """지식베이스 초기 데이터 로드"""
        # 기존 데이터가 있는지 확인
        if self.collection.count() > 0:
            logger.info("지식베이스에 기존 데이터가 있습니다.")
            return
        
        # 개인정보 탐지 관련 지식 데이터
        knowledge_data = [
            {
                "content": "주민등록번호는 YYMMDD-ABCDEFG 형식으로, 생년월일 6자리와 성별/세대코드 1자리, 나머지 6자리로 구성됩니다.",
                "metadata": {"type": "rrn", "category": "pattern", "description": "주민등록번호 형식 설명"},
                "examples": ["901201-1234567", "850315-2345678", "950712-3456789"]
            },
            {
                "content": "한국 전화번호는 010, 011, 016, 017, 018, 019로 시작하는 휴대폰 번호와 02(서울), 031-065(지역번호)로 시작하는 유선전화가 있습니다.",
                "metadata": {"type": "phone", "category": "pattern", "description": "한국 전화번호 형식"},
                "examples": ["010-1234-5678", "02-1234-5678", "031-123-4567"]
            },
            {
                "content": "이메일 주소는 로컬파트@도메인 형식으로, 로컬파트에는 영문, 숫자, 특수문자(._%+-)가 포함될 수 있습니다.",
                "metadata": {"type": "email", "category": "pattern", "description": "이메일 주소 형식"},
                "examples": ["user@example.com", "test.email+tag@domain.co.kr", "admin123@company.org"]
            },
            {
                "content": "계좌번호는 일반적으로 9-14자리 숫자로 구성되며, 하이픈이나 공백으로 구분될 수 있습니다.",
                "metadata": {"type": "account", "category": "pattern", "description": "계좌번호 형식"},
                "examples": ["123-456-789012", "1234567890123", "12-3456-7890-1234"]
            },
            {
                "content": "한국 성명은 일반적으로 2-4자의 한글로 구성되며, 흔한 성씨(김, 이, 박, 최 등)와 이름으로 이루어집니다.",
                "metadata": {"type": "name", "category": "pattern", "description": "한국 성명 형식"},
                "examples": ["김철수", "이영희", "박민수", "최지영"]
            },
            {
                "content": "한국 주소는 시/도, 시/군/구, 읍/면, 동/리, 도로명/지번, 건물번호 순으로 구성됩니다.",
                "metadata": {"type": "address", "category": "pattern", "description": "한국 주소 형식"},
                "examples": ["서울특별시 강남구 테헤란로 123", "부산광역시 해운대구 센텀중앙로 456"]
            },
            {
                "content": "개인정보는 개인을 식별할 수 있는 모든 정보로, 이름, 주민등록번호, 연락처, 이메일, 주소, 계좌번호 등이 포함됩니다.",
                "metadata": {"type": "general", "category": "definition", "description": "개인정보 정의"},
                "examples": []
            },
            {
                "content": "개인정보가 아닌 정보는 일반적인 직업명, 나이대, 지역명(시/도 단위), 성별 등 개인을 식별할 수 없는 정보입니다.",
                "metadata": {"type": "general", "category": "non_pii", "description": "개인정보가 아닌 정보"},
                "examples": ["개발자", "30대", "서울시", "남성"]
            }
        ]
        
        # 지식 데이터를 VectorDB에 저장
        self._add_knowledge_batch(knowledge_data)
        logger.info(f"초기 지식베이스 데이터 {len(knowledge_data)}개 항목 추가됨")
    
    def _add_knowledge_batch(self, knowledge_data: List[Dict[str, Any]]):
        """지식 데이터를 VectorDB에 배치로 추가"""
        contents = []
        metadatas = []
        ids = []
        
        for i, item in enumerate(knowledge_data):
            content = item["content"]
            metadata = item["metadata"].copy()
            metadata["examples"] = json.dumps(item.get("examples", []), ensure_ascii=False)
            metadata["created_at"] = datetime.now().isoformat()
            
            # 고유 ID 생성
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            doc_id = f"{metadata['type']}_{metadata['category']}_{content_hash}"
            
            contents.append(content)
            metadatas.append(metadata)
            ids.append(doc_id)
        
        # 임베딩 생성 및 저장
        embeddings = self.embedding_model.encode(contents).tolist()
        
        self.collection.add(
            documents=contents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        logger.info(f"{len(knowledge_data)}개 지식 항목이 VectorDB에 추가됨")
    
    def add_detection_result(self, text: str, detection_result: Dict[str, Any], context: str = ""):
        """개인정보 탐지 결과를 지식베이스에 추가"""
        content = f"탐지된 텍스트: {text}\n탐지 결과: {json.dumps(detection_result, ensure_ascii=False)}\n컨텍스트: {context}"
        
        metadata = {
            "type": "detection_result",
            "category": "case",
            "description": "개인정보 탐지 사례",
            "detected_types": json.dumps(detection_result.get("types", []), ensure_ascii=False),
            "confidence": detection_result.get("confidence", 0.0),
            "created_at": datetime.now().isoformat()
        }
        
        # 고유 ID 생성
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        doc_id = f"detection_{text_hash}_{int(datetime.now().timestamp())}"
        
        # 임베딩 생성 및 저장
        embedding = self.embedding_model.encode([content])[0].tolist()
        
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id],
            embeddings=[embedding]
        )
        
        logger.info(f"탐지 결과가 지식베이스에 추가됨: {doc_id}")
    
    def search_relevant_knowledge(self, query: str, n_results: int = 5, filter_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """관련 지식 검색"""
        # 쿼리 임베딩 생성
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # 검색 옵션 설정
        where_clause = None
        if filter_types:
            where_clause = {"type": {"$in": filter_types}}
        
        # 유사도 검색 수행
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause
        )
        
        # 결과 포맷팅
        formatted_results = []
        for i in range(len(results["documents"][0])):
            result = {
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "id": results["ids"][0][i]
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def get_detection_context(self, text: str, detected_types: List[str]) -> str:
        """개인정보 탐지를 위한 컨텍스트 정보 생성"""
        # 탐지된 유형에 따른 관련 지식 검색
        relevant_knowledge = self.search_relevant_knowledge(
            query=text,
            n_results=3,
            filter_types=detected_types + ["general"]
        )
        
        # 컨텍스트 구성
        context_parts = []
        for knowledge in relevant_knowledge:
            content = knowledge["content"]
            metadata = knowledge["metadata"]
            
            if metadata.get("category") == "pattern":
                context_parts.append(f"패턴 정보: {content}")
            elif metadata.get("category") == "definition":
                context_parts.append(f"정의: {content}")
            elif metadata.get("category") == "case":
                context_parts.append(f"탐지 사례: {content}")
        
        return "\n".join(context_parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """지식베이스 통계 정보 반환"""
        total_count = self.collection.count()
        
        # 유형별 통계
        type_stats = {}
        all_metadata = self.collection.get()["metadatas"]
        
        for metadata in all_metadata:
            pii_type = metadata.get("type", "unknown")
            category = metadata.get("category", "unknown")
            key = f"{pii_type}_{category}"
            type_stats[key] = type_stats.get(key, 0) + 1
        
        return {
            "total_documents": total_count,
            "type_statistics": type_stats,
            "collection_name": self.collection_name
        }


class RAGService:
    """RAG 서비스 메인 클래스"""
    
    def __init__(self, persist_directory: str = "./vectordb"):
        """RAG 서비스 초기화"""
        self.knowledge_base = PIIKnowledgeBase(persist_directory)
        logger.info("RAG 서비스 초기화 완료")
    
    def enhance_detection_with_rag(self, text: str, detected_types: List[str]) -> Dict[str, Any]:
        """RAG를 활용한 개인정보 탐지 향상"""
        # 관련 지식 검색
        context = self.knowledge_base.get_detection_context(text, detected_types)
        
        # 탐지 결과 구성
        result = {
            "text": text,
            "detected_types": detected_types,
            "context": context,
            "enhanced": True,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def store_detection_case(self, text: str, detection_result: Dict[str, Any], context: str = ""):
        """탐지 사례를 지식베이스에 저장"""
        self.knowledge_base.add_detection_result(text, detection_result, context)
    
    def search_similar_cases(self, text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """유사한 탐지 사례 검색"""
        return self.knowledge_base.search_relevant_knowledge(
            query=text,
            n_results=n_results,
            filter_types=["detection_result"]
        )
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """지식베이스 통계 정보 반환"""
        return self.knowledge_base.get_statistics()


# 전역 RAG 서비스 인스턴스
_rag_service = None

def get_rag_service() -> RAGService:
    """RAG 서비스 싱글톤 인스턴스 반환"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

def initialize_rag_service(persist_directory: str = "./vectordb") -> RAGService:
    """RAG 서비스 초기화"""
    global _rag_service
    _rag_service = RAGService(persist_directory)
    return _rag_service
