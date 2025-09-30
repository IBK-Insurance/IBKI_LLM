# RAG (Retrieval-Augmented Generation) 모듈

개인정보 탐지를 위한 RAG 모듈로, VectorDB를 활용하여 상세한 개인정보 탐지 지식베이스를 구축하고 LLM과 연동하여 탐지 정확도를 향상시킵니다.

## 주요 기능

### 1. VectorDB 기반 지식베이스
- **ChromaDB**를 활용한 벡터 데이터베이스
- 개인정보 탐지 패턴 및 예시 저장
- 유사도 검색을 통한 관련 정보 검색

### 2. 임베딩 서비스
- **Sentence Transformers**를 활용한 텍스트 벡터화
- 다국어 지원 (한국어 최적화)
- 실시간 임베딩 생성 및 검색

### 3. 지식베이스 관리
- 개인정보 탐지 패턴 자동 수집
- 탐지 사례 학습 및 저장
- 지식베이스 통계 및 관리 기능

### 4. LLM 연동
- 기존 `check_personal_info` 메소드와 통합
- RAG를 활용한 컨텍스트 정보 제공
- 유사 사례 기반 탐지 정확도 향상

## 설치 및 설정

### 1. 필요한 라이브러리 설치

```bash
pip install -r requirements_rag.txt
```

### 2. 환경 설정

```python
# .env 파일에 추가 (선택사항)
RAG_VECTORDB_PATH=./vectordb
RAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

## 사용법

### 1. 기본 사용법

```python
from server.llm_service import check_personal_info

# RAG가 통합된 개인정보 탐지
text = "제 이름은 김철수이고, 전화번호는 010-1234-5678입니다."
result = check_personal_info(text)
print(result)
```

### 2. RAG 서비스 직접 사용

```python
from server.rag_service import get_rag_service

# RAG 서비스 초기화
rag_service = get_rag_service()

# 지식베이스 검색
results = rag_service.knowledge_base.search_relevant_knowledge(
    query="주민등록번호",
    n_results=5
)

# 탐지 사례 저장
detection_result = {
    "types": ["rrn", "phone"],
    "confidence": 0.9,
    "method": "regex_pattern"
}
rag_service.store_detection_case(text, detection_result)
```

### 3. RAG 관리자 사용

```python
from server.rag_manager import RAGManager

# RAG 관리자 초기화
rag_manager = RAGManager()

# 지식베이스 통계 조회
stats = rag_manager.get_knowledge_statistics()
print(f"총 문서 수: {stats['data']['total_documents']}")

# 지식 검색
search_result = rag_manager.search_knowledge("전화번호", n_results=3)

# 탐지 이력 조회
history = rag_manager.get_detection_history(limit=10)
```

## 모듈 구조

```
server/
├── rag_service.py      # RAG 서비스 메인 모듈
├── rag_manager.py       # RAG 관리 유틸리티
├── rag_config.py        # RAG 설정 파일
├── llm_service.py       # LLM 서비스 (RAG 통합)
└── pii_detector.py      # 기존 PII 탐지 모듈
```

## 주요 클래스

### 1. PIIKnowledgeBase
- VectorDB 관리
- 임베딩 생성 및 검색
- 지식베이스 초기화

### 2. RAGService
- RAG 서비스 메인 클래스
- 탐지 결과 저장 및 검색
- LLM 연동

### 3. RAGManager
- 지식베이스 관리
- 통계 정보 조회
- 데이터 백업 및 복원

## 설정 옵션

### VectorDB 설정
```python
# rag_config.py에서 설정 가능
RAG_CONFIG = {
    "vectordb": {
        "persist_directory": "./vectordb",
        "collection_name": "pii_detection_knowledge",
        "anonymized_telemetry": False
    }
}
```

### 임베딩 모델 설정
```python
RAG_CONFIG = {
    "embedding": {
        "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "max_seq_length": 512,
        "device": "cpu"
    }
}
```

## 테스트

### 1. 통합 테스트 실행

```bash
python test_rag_integration.py
```

### 2. 개별 모듈 테스트

```python
# RAG 서비스 테스트
from server.rag_service import get_rag_service
rag_service = get_rag_service()
stats = rag_service.get_knowledge_statistics()

# RAG 관리자 테스트
from server.rag_manager import RAGManager
rag_manager = RAGManager()
search_result = rag_manager.search_knowledge("주민등록번호")
```

## 성능 최적화

### 1. 임베딩 모델 선택
- **경량 모델**: `paraphrase-multilingual-MiniLM-L12-v2` (기본)
- **고성능 모델**: `paraphrase-multilingual-mpnet-base-v2`
- **한국어 특화**: `jhgan/ko-sroberta-multitask`

### 2. VectorDB 최적화
- 인덱스 설정 최적화
- 배치 처리로 성능 향상
- 메모리 사용량 모니터링

### 3. 검색 성능
- 유사도 임계값 조정
- 결과 개수 제한
- 캐싱 활용

## 문제 해결

### 1. 라이브러리 설치 오류
```bash
# ChromaDB 설치 문제
pip install --upgrade pip
pip install chromadb

# Sentence Transformers 설치 문제
pip install sentence-transformers
```

### 2. 메모리 부족
```python
# 임베딩 모델을 더 작은 모델로 변경
RAG_CONFIG["embedding"]["model_name"] = "paraphrase-multilingual-MiniLM-L12-v2"
```

### 3. VectorDB 접근 오류
```python
# VectorDB 경로 확인 및 권한 설정
import os
os.makedirs("./vectordb", exist_ok=True)
```

## 확장 가능성

### 1. 추가 개인정보 유형
- 새로운 PII 유형 추가
- 탐지 패턴 확장
- 예시 데이터 보강

### 2. 다국어 지원
- 영어, 중국어 등 다국어 탐지
- 언어별 임베딩 모델
- 다국어 지식베이스

### 3. 고급 기능
- 실시간 학습
- 사용자 피드백 반영
- 탐지 정확도 분석

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.
