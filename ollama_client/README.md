# Ollama API 클라이언트

이 프로젝트는 Ollama API와 상호작용하기 위한 Python 클라이언트입니다. 대화 기록을 유지하면서 LLM 모델과 대화할 수 있는 기능을 제공합니다.

## 기능

- Ollama API를 통한 LLM 모델과의 대화
- 대화 기록 유지 및 컨텍스트 관리
- CLI 인터페이스를 통한 쉬운 사용
- 모델 관리 기능 (목록 조회, 다운로드, 삭제)

## 설치 방법

1. 저장소를 클론합니다:
```bash
git clone [repository-url]
cd ollama_client
```

2. 가상환경을 생성하고 활성화합니다:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 필요한 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

## 사용 방법

### CLI 사용

1. 대화형 채팅 인터페이스:
```bash
python -m src.cli chat --model gemma3 --session-id my_session
```

2. 사용 가능한 모델 목록 표시:
```bash
python -m src.cli list-models
```

3. 모델 다운로드:
```bash
python -m src.cli pull-model llama2
```

4. 모델 삭제:
```bash
python -m src.cli delete-model llama2
```

### Python 코드에서 사용

```python
from src.ollama_client import OllamaClient

# 클라이언트 초기화
client = OllamaClient()

# 대화 생성
response = client.generate(
    prompt="안녕하세요! 오늘 날씨에 대해 이야기해볼까요?",
    model="gemma3",
    session_id="my_session"
)

print(response)

# 대화 기록 유지하면서 추가 메시지
response = client.generate(
    prompt="비 오는 날을 좋아해요",
    model="gemma3",
    session_id="my_session"
)

print(response)
```

## 예제 실행

예제 스크립트를 실행하여 클라이언트 사용법을 확인할 수 있습니다:

```bash
python -m src.example
```

## 주의사항

- Ollama 서버가 실행 중이어야 합니다.
- 기본적으로 `http://localhost:11434`에서 Ollama API를 호출합니다.
- 다른 URL을 사용하려면 `OllamaClient` 초기화 시 `base_url` 매개변수를 지정하세요. 