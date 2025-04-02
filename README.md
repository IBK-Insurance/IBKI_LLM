# Ollama LLM Web Interface

이 프로젝트는 Ollama를 사용하여 LLM 모델과 상호작용할 수 있는 웹 인터페이스를 제공합니다.

## Prerequisites

- Python 3.8 이상
- Ollama가 설치되어 있어야 합니다 (https://ollama.ai/)
- 원하는 LLM 모델이 Ollama에 설치되어 있어야 합니다 (예: llama2)

## 설치 방법

1. 저장소를 클론합니다:
```bash
git clone [repository-url]
cd [repository-name]
```

2. 필요한 Python 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

3. Ollama를 설치하고 원하는 모델을 다운로드합니다:
```bash
# Ollama 설치 후
ollama pull llama2  # 또는 다른 원하는 모델
```

## 실행 방법

1. Ollama 서버가 실행 중인지 확인합니다:
```bash
ollama serve
```

2. 웹 애플리케이션을 실행합니다:
```bash
python app.py
```

3. 웹 브라우저에서 http://localhost:8000 으로 접속합니다.

## 기능

- 실시간 채팅 인터페이스
- Ollama LLM 모델과의 상호작용
- 반응형 디자인
- 에러 처리

## 주의사항

- Ollama 서버가 실행 중이어야 합니다.
- 기본적으로 llama2 모델을 사용하도록 설정되어 있습니다. 다른 모델을 사용하려면 app.py 파일의 model 파라미터를 수정하세요. 