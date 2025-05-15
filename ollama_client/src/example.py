from ollama_client import OllamaClient

def main():
    # Ollama 클라이언트 초기화
    client = OllamaClient()
    
    # 사용 가능한 모델 목록 가져오기
    print("사용 가능한 모델 목록:")
    try:
        models = client.list_models()
        for model in models:
            print(f"- {model['name']}")
    except Exception as e:
        print(f"모델 목록 가져오기 오류: {str(e)}")
    
    # 대화 세션 ID
    session_id = "example_session"
    
    # 첫 번째 메시지
    prompt1 = "안녕하세요! 오늘 날씨에 대해 이야기해볼까요?"
    print(f"\n사용자: {prompt1}")
    
    try:
        response1 = client.generate(
            prompt=prompt1,
            model="gemma3",
            session_id=session_id
        )
        print(f"어시스턴트: {response1}")
    except Exception as e:
        print(f"응답 생성 오류: {str(e)}")
    
    # 두 번째 메시지 (대화 컨텍스트 유지)
    prompt2 = "비 오는 날을 좋아해요"
    print(f"\n사용자: {prompt2}")
    
    try:
        response2 = client.generate(
            prompt=prompt2,
            model="gemma3",
            session_id=session_id
        )
        print(f"어시스턴트: {response2}")
    except Exception as e:
        print(f"응답 생성 오류: {str(e)}")
    
    # 세 번째 메시지 (대화 컨텍스트 유지)
    prompt3 = "비 오는 날에 특별히 좋아하시는 활동이 있으신가요?"
    print(f"\n사용자: {prompt3}")
    
    try:
        response3 = client.generate(
            prompt=prompt3,
            model="gemma3",
            session_id=session_id
        )
        print(f"어시스턴트: {response3}")
    except Exception as e:
        print(f"응답 생성 오류: {str(e)}")

if __name__ == "__main__":
    main() 