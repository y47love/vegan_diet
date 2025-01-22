import requests

def detect_food(image_path, api_url="http://localhost:8000/predict"):
    # 이미지 파일 열기
    with open(image_path, "rb") as f:
        files = {"file": f}
        # API 호출
        response = requests.post(api_url, files=files)
    
    if response.status_code == 200:
        results = response.json()
        # 결과 출력
        for detection in results["detections"]:
            print(f"음식: {detection['class_name']}")
            print(f"확률: {detection['confidence']:.2f}")
            print("---")
    else:
        print("Error:", response.status_code)

# 사용 예시
detect_food("test_meal.jpg")