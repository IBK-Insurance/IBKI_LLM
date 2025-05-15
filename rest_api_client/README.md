# REST API Client

간단한 REST API 클라이언트 프로젝트입니다. 이 프로젝트는 외부 API를 호출하기 위한 기본적인 기능을 제공합니다.

## 설치 방법

1. 프로젝트 클론:
```bash
git clone <repository-url>
cd rest_api_client
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

3. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정:
```bash
cp .env.example .env
```
그리고 `.env` 파일을 편집하여 실제 API 설정값을 입력하세요.

## 사용 방법

1. API 클라이언트 초기화:
```python
from api_client import APIClient

client = APIClient(base_url="https://api.example.com", api_key="your_api_key")
```

2. 로그인 인증:
```python
success, message = client.login("username", "password")
if success:
    # API 호출
```

3. API 호출 예제:
```python
# GET 요청
response = client.get('endpoint')

# POST 요청
data = {"key": "value"}
response = client.post('endpoint', data=data)

# PUT 요청
data = {"key": "updated_value"}
response = client.put('endpoint', data=data)

# DELETE 요청
response = client.delete('endpoint')
```

4. 동적 파라미터 사용:
```python
# 경로 파라미터 사용
path_params = {'user_id': '123'}
response = client.get('users/{user_id}/profile', path_params=path_params)

# 쿼리 파라미터 사용
query_params = {'limit': 10, 'offset': 0, 'sort': 'name', 'order': 'asc'}
response = client.get('users', params=query_params)

# 커스텀 헤더 사용
headers = {'X-Custom-Header': 'value'}
response = client.post('endpoint', data=data, headers=headers)

# JSON이 아닌 데이터 전송
response = client.post('endpoint', data=form_data, json_data=False)
```

5. 파일 다운로드:
```python
downloaded_file = client.download_file('files/{file_id}', 'downloads/file.pdf', path_params={'file_id': '123'})
```

6. 로그아웃:
```python
success, message = client.logout()
```

## 명령줄 인터페이스

프로젝트는 명령줄 인터페이스를 제공하여 동적 파라미터를 쉽게 사용할 수 있습니다:

```bash
python main.py --user-id 123 --resource-id 456 --file-id 789 --limit 20 --offset 0 --sort name --order desc
```

사용 가능한 옵션:
- `--user-id`: 사용자 ID
- `--resource-id`: 리소스 ID
- `--file-id`: 파일 ID
- `--limit`: 페이지네이션 제한 (기본값: 10)
- `--offset`: 페이지네이션 오프셋 (기본값: 0)
- `--sort`: 정렬 필드 (기본값: id)
- `--order`: 정렬 순서 (asc 또는 desc, 기본값: asc)

## 주요 기능

- GET, POST, PUT, DELETE 메서드 지원
- 자동 JSON 직렬화/역직렬화
- API 키 인증 지원
- 로그인/로그아웃 기능
- 경로 파라미터 지원
- 쿼리 파라미터 지원
- 커스텀 헤더 지원
- 파일 다운로드 기능
- 환경 변수를 통한 설정 관리

## 라이선스

MIT License 