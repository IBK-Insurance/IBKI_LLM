# IBKI 개인정보 가드레일 시스템

이 프로젝트는 개인정보 보호를 위한 가드레일 시스템으로, 텍스트와 이미지에서 개인정보를 탐지하고 ChatGPT와 연동하여 분석을 제공합니다.

## 🏗️ 프로젝트 구조

```
ibki_sys_guardrail/
├── client/                    # UI 레이아웃 및 사용자 인터랙션
│   ├── __init__.py
│   ├── ui_components.py       # 재사용 가능한 UI 컴포넌트
│   ├── text_input_section.py  # 텍스트 입력 섹션
│   ├── image_input_section.py # 이미지 입력 섹션
│   └── chat_section.py        # ChatGPT 대화 섹션
├── server/                    # 비즈니스 로직 및 API 처리
│   ├── __init__.py
│   ├── llm_service.py         # LLM 서비스 (Ollama)
│   ├── openai_service.py      # OpenAI 서비스 (ChatGPT)
│   ├── file_service.py        # 파일 처리 서비스
│   └── system_service.py      # 시스템 상태 관리
└── personal_info_app.py       # 메인 애플리케이션
```

## 📋 Prerequisites

- Python 3.8 이상
- Ollama가 설치되어 있어야 합니다 (https://ollama.ai/)
- qwen2.5vl:7b 모델이 Ollama에 설치되어 있어야 합니다
- OpenAI API 키 (선택사항, ChatGPT 기능 사용 시)

## 🚀 설치 방법

1. 저장소를 클론합니다:
```bash
git clone [repository-url]
cd IBKI_LLM
```

2. 가상환경을 생성하고 활성화합니다:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 필요한 Python 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

4. Ollama를 설치하고 qwen2.5vl 모델을 다운로드합니다:
```bash
# Ollama 설치 후
ollama pull qwen2.5vl:7b
```

5. 환경설정 파일을 생성합니다:
```bash
# .env 파일 생성
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

## 🎯 실행 방법

1. Ollama 서버가 실행 중인지 확인합니다:
```bash
ollama serve
```

2. Streamlit 애플리케이션을 실행합니다:
```bash
streamlit run ibki_sys_guardrail/personal_info_app.py
```

3. 웹 브라우저에서 http://localhost:8501 으로 접속합니다.

## ✨ 주요 기능

### 🔍 개인정보 탐지
- **텍스트 분석**: 직접 입력한 텍스트에서 개인정보 탐지
- **이미지 분석**: 업로드한 이미지에서 텍스트 추출 후 개인정보 탐지
- **멀티모달 LLM**: qwen2.5vl 모델을 활용한 이미지 텍스트 추출

### 💬 ChatGPT 연동
- 개인정보가 포함되지 않은 경우 자동으로 ChatGPT 분석 제공
- 독립적인 ChatGPT 대화 기능
- 대화 히스토리 관리

### 🎨 사용자 친화적 UI
- 모듈화된 UI 컴포넌트
- 실시간 시스템 상태 확인
- 반응형 디자인

## 🔧 개발 및 수정

### UI 레이아웃 수정
UI 관련 수정은 `client/` 디렉토리에서 진행하세요:

- **전체 UI 컴포넌트**: `client/ui_components.py`
- **텍스트 입력 섹션**: `client/text_input_section.py`
- **이미지 입력 섹션**: `client/image_input_section.py`
- **ChatGPT 대화 섹션**: `client/chat_section.py`

### 비즈니스 로직 수정
비즈니스 로직 수정은 `server/` 디렉토리에서 진행하세요:

- **LLM 서비스**: `server/llm_service.py`
- **OpenAI 서비스**: `server/openai_service.py`
- **파일 처리**: `server/file_service.py`
- **시스템 관리**: `server/system_service.py`

## ⚠️ 주의사항

- Ollama 서버가 실행 중이어야 합니다.
- 이 도구는 참고용이며, 법적 판단의 근거로 사용하지 마세요.
- 실제 개인정보 처리 시에는 관련 법규를 준수하세요.
- OpenAI API 키는 선택사항이지만, ChatGPT 기능 사용 시 필요합니다.

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **LLM**: Ollama (qwen2.5vl:7b)
- **AI Service**: OpenAI GPT-4o
- **Image Processing**: PIL (Pillow)
- **File Processing**: PyPDF2, python-docx
- **Environment**: python-dotenv 