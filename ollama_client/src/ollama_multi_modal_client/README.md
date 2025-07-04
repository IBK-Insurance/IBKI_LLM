# Qwen2.5-VL-3B 멀티모달 웹 클라이언트

이 프로젝트는 Ollama에서 실행되는 Qwen2.5-VL-3B 모델을 사용하여 이미지와 텍스트를 함께 처리할 수 있는 웹 인터페이스를 제공합니다.

## 사전 요구사항

1. Ollama가 설치되어 있어야 합니다.
2. Qwen2.5-VL-3B 모델이 Ollama에 설치되어 있어야 합니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. Ollama에서 Qwen2.5-VL-3B 모델 다운로드:
```bash
ollama pull qwen2.5-vl-3b
```

## 실행 방법

1. Ollama 서버가 실행 중인지 확인합니다:
```bash
ollama serve
```

2. 웹 클라이언트 실행:
```bash
streamlit run app.py
```

## 사용 방법

1. 웹 브라우저에서 `http://localhost:8501`로 접속합니다.
2. "이미지를 업로드하세요" 섹션에서 이미지 파일을 선택합니다.
3. "질문을 입력하세요" 텍스트 영역에 이미지에 대한 질문을 입력합니다.
4. "생성" 버튼을 클릭하여 응답을 받습니다.

## 주의사항

- 이미지는 JPG, JPEG, PNG 형식만 지원됩니다.
- Ollama 서버가 실행 중이어야 합니다.
- 이미지 크기가 너무 크면 처리 시간이 길어질 수 있습니다. 