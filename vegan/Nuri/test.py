from ultralytics import YOLO
import os
import pandas as pd

def evaluate_model(model_path, data_yaml, test_images):
    """
    모델의 성능을 테스트 데이터셋에서 평가하는 함수
    
    Args:
        model_path (str): 모델 가중치 파일 경로 (.pt 파일)
        data_yaml (str): 데이터셋 yaml 파일 경로
        test_images (str): 테스트 이미지가 포함된 디렉토리 경로

    Returns:
        dict: 모델 평가 지표 (Precision, Recall, mAP 등)
    """
    print(f"Evaluating model: {model_path}")
    model = YOLO(model_path)

    # 모델 평가
    metrics = model.val(
        data=data_yaml,  # 데이터셋 정의 파일
        imgsz=640,       # 평가 시 사용할 입력 이미지 크기
        save=False,      # 평가 결과 저장 여부
        batch=16         # 배치 크기
    )
    
    # 주요 성능 지표 출력
    results = {
        'Precision': metrics.box.map_precision,
        'Recall': metrics.box.map_recall,
        'mAP@50': metrics.map50,
        'mAP@50-95': metrics.map
    }
    
    return results

def main():
    # 경로 설정
    BASE_DIR = "C:/Users/Admin/Desktop/VGFD/runs/detect/train/weights"
    DATA_YAML = "C:/Users/Admin/Desktop/VGFD/yolo_dataset/dataset.yaml"  # 데이터셋 yaml 파일
    TEST_IMAGES = "C:/Users/Admin/Desktop/VGFD/yolo_dataset/val/images"  # 테스트 이미지 디렉토리

    # 모델 경로
    best_model_path = os.path.join(BASE_DIR, "best.pt")
    last_model_path = os.path.join(BASE_DIR, "last.pt")
    
    # 성능 평가
    print("=== Evaluating best.pt ===")
    best_results = evaluate_model(best_model_path, DATA_YAML, TEST_IMAGES)
    print("\n=== Evaluating last.pt ===")
    last_results = evaluate_model(last_model_path, DATA_YAML, TEST_IMAGES)

    # 결과 비교
    print("\n=== Model Performance Comparison ===")
    results_df = pd.DataFrame([best_results, last_results], index=["best.pt", "last.pt"])
    print(results_df)

if __name__ == "__main__":
    main()
