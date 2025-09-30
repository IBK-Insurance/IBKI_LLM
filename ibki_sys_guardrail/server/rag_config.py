"""
RAG 서비스 설정 파일
- VectorDB 설정
- 임베딩 모델 설정
- 지식베이스 초기화 설정
"""

import os
from pathlib import Path
from typing import Dict, Any, List

# RAG 서비스 기본 설정
RAG_CONFIG = {
    # VectorDB 설정
    "vectordb": {
        "persist_directory": "./vectordb",
        "collection_name": "pii_detection_knowledge",
        "anonymized_telemetry": False
    },
    
    # 임베딩 모델 설정
    "embedding": {
        "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "max_seq_length": 512,
        "device": "cpu"  # "cuda" if available
    },
    
    # 검색 설정
    "search": {
        "default_n_results": 5,
        "similarity_threshold": 0.7,
        "max_context_length": 1000
    },
    
    # 지식베이스 초기화 설정
    "knowledge_base": {
        "auto_initialize": True,
        "include_examples": True,
        "include_patterns": True,
        "include_definitions": True
    }
}

# 개인정보 유형별 설정
PII_TYPE_CONFIG = {
    "rrn": {
        "korean_name": "주민등록번호",
        "description": "개인을 식별할 수 있는 고유 번호",
        "pattern_examples": ["901201-1234567", "850315-2345678"],
        "detection_priority": 5
    },
    "phone": {
        "korean_name": "전화번호",
        "description": "개인 연락처 정보",
        "pattern_examples": ["010-1234-5678", "02-1234-5678"],
        "detection_priority": 4
    },
    "email": {
        "korean_name": "이메일",
        "description": "개인 이메일 주소",
        "pattern_examples": ["user@example.com", "test@domain.co.kr"],
        "detection_priority": 4
    },
    "account": {
        "korean_name": "계좌번호",
        "description": "금융 계좌 정보",
        "pattern_examples": ["123-456-789012", "1234567890123"],
        "detection_priority": 3
    },
    "name": {
        "korean_name": "성명",
        "description": "개인 이름",
        "pattern_examples": ["김철수", "이영희"],
        "detection_priority": 2
    },
    "address": {
        "korean_name": "주소",
        "description": "개인 거주지 정보",
        "pattern_examples": ["서울특별시 강남구", "부산광역시 해운대구"],
        "detection_priority": 2
    }
}

# 지식베이스 초기 데이터 템플릿
KNOWLEDGE_TEMPLATES = {
    "patterns": [
        {
            "content": "{description}",
            "metadata": {
                "type": "{pii_type}",
                "category": "pattern",
                "description": "{korean_name} 패턴 설명"
            },
            "examples": "{pattern_examples}"
        }
    ],
    "definitions": [
        {
            "content": "개인정보는 개인을 식별할 수 있는 모든 정보로, {korean_name} 등이 포함됩니다.",
            "metadata": {
                "type": "general",
                "category": "definition",
                "description": "개인정보 정의"
            },
            "examples": []
        }
    ],
    "non_pii": [
        {
            "content": "개인정보가 아닌 정보는 일반적인 직업명, 나이대, 지역명(시/도 단위), 성별 등 개인을 식별할 수 없는 정보입니다.",
            "metadata": {
                "type": "general",
                "category": "non_pii",
                "description": "개인정보가 아닌 정보"
            },
            "examples": ["개발자", "30대", "서울시", "남성"]
        }
    ]
}

def get_rag_config() -> Dict[str, Any]:
    """RAG 설정 반환"""
    return RAG_CONFIG.copy()

def get_pii_type_config() -> Dict[str, Any]:
    """개인정보 유형별 설정 반환"""
    return PII_TYPE_CONFIG.copy()

def get_knowledge_templates() -> Dict[str, List[Dict[str, Any]]]:
    """지식베이스 템플릿 반환"""
    return KNOWLEDGE_TEMPLATES.copy()

def update_rag_config(key: str, value: Any) -> bool:
    """RAG 설정 업데이트"""
    try:
        keys = key.split('.')
        config = RAG_CONFIG
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        return True
    except Exception:
        return False

def get_vectordb_path() -> Path:
    """VectorDB 저장 경로 반환"""
    return Path(RAG_CONFIG["vectordb"]["persist_directory"])

def get_embedding_model_name() -> str:
    """임베딩 모델명 반환"""
    return RAG_CONFIG["embedding"]["model_name"]

def get_collection_name() -> str:
    """컬렉션명 반환"""
    return RAG_CONFIG["vectordb"]["collection_name"]

def is_auto_initialize() -> bool:
    """자동 초기화 여부 반환"""
    return RAG_CONFIG["knowledge_base"]["auto_initialize"]

def get_search_config() -> Dict[str, Any]:
    """검색 설정 반환"""
    return RAG_CONFIG["search"].copy()

def get_pii_type_korean_name(pii_type: str) -> str:
    """개인정보 유형의 한국어 이름 반환"""
    return PII_TYPE_CONFIG.get(pii_type, {}).get("korean_name", pii_type)

def get_pii_type_description(pii_type: str) -> str:
    """개인정보 유형 설명 반환"""
    return PII_TYPE_CONFIG.get(pii_type, {}).get("description", "")

def get_pii_type_priority(pii_type: str) -> int:
    """개인정보 유형 우선순위 반환"""
    return PII_TYPE_CONFIG.get(pii_type, {}).get("detection_priority", 1)

def get_all_pii_types() -> List[str]:
    """모든 개인정보 유형 리스트 반환"""
    return list(PII_TYPE_CONFIG.keys())

def get_pii_type_examples(pii_type: str) -> List[str]:
    """개인정보 유형 예시 반환"""
    return PII_TYPE_CONFIG.get(pii_type, {}).get("pattern_examples", [])
