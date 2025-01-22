from ultralytics import YOLO
import os
import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
from pathlib import Path
import yaml
import shutil
from datetime import datetime
import matplotlib.pyplot as plt
import torch
torch.cuda.empty_cache()


import warnings
warnings.filterwarnings('ignore', category=UserWarning)

class DatasetPreparator:
    def __init__(self, data_dir, output_dir):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.class_names = self._get_class_names()
        
    def _get_class_names(self):
        return sorted([folder.name for folder in self.data_dir.iterdir() if folder.is_dir()])
    
    def prepare_yolo_dataset(self, train_ratio=0.8):
        # YOLO 데이터셋 구조 생성
        train_dir = self.output_dir / 'train'
        val_dir = self.output_dir / 'val'    # 'val'로 수정 (validation의 약자)

        # 기존 디렉토리 삭제 후 새로 생성
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)

        for d in [train_dir / 'images', train_dir / 'labels',
                val_dir / 'images', val_dir / 'labels']:
            d.mkdir(parents=True, exist_ok=True)

            for d in [train_dir / 'images', train_dir / 'labels',
                    val_dir / 'images', val_dir / 'labels']:
                d.mkdir(parents=True, exist_ok=True)

            # 클래스별 데이터 처리
        for idx, class_name in enumerate(self.class_names):
            print(f"Processing {class_name}...")
            class_dir = self.data_dir / class_name

            # 이미지 파일 찾기 (대소문자 구분 없이, 재귀적 탐색)
            images = []
            for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
                images.extend(list(class_dir.rglob(f'*{ext}')))  # rglob으로 변경하여 재귀적 탐색

            if not images:
                print(f"Warning: No images found in {class_dir}")
                continue
                
            # 이미지 경로 확인
            valid_images = []
            for img_path in images:
                if os.path.exists(img_path):
                    valid_images.append(img_path)
                else:
                    print(f"Warning: Image not found: {img_path}")

            # 이미지 셔플
            np.random.shuffle(valid_images)
            split_idx = int(len(valid_images) * train_ratio)

            # 학습/검증 데이터 분할
            train_images = valid_images[:split_idx]
            val_images = valid_images[split_idx:]

            # 이미지 처리
            self._process_image_set(train_images, train_dir, idx)
            self._process_image_set(val_images, val_dir, idx)

        # yaml 파일 생성
        self._create_yaml_file()
        
        print("Dataset preparation completed!")
        
    def _process_image_set(self, images, output_dir, class_idx):
        for img_path in images:
            try:
                # 이미지 복사
                shutil.copy2(img_path, output_dir / 'images' / img_path.name)

                # 이미지 읽기
                img = cv2.imread(str(img_path))
                if img is None:
                    print(f"Warning: Could not read image {img_path}")
                    continue
                    
                h, w = img.shape[:2]

                # YOLO 포맷의 바운딩 박스 생성 (전체 이미지)
                label_content = f"{class_idx} 0.5 0.5 1.0 1.0"

                # 레이블 파일 저장
                label_path = output_dir / 'labels' / (img_path.stem + '.txt')
                with open(label_path, 'w') as f:
                    f.write(label_content)

            except Exception as e:
                print(f"Error processing {img_path}: {str(e)}")
                continue
    
    def _create_yaml_file(self):
        yaml_content = {
            'path': str(self.output_dir.absolute()),  # 절대 경로 사용
            'train': str(self.output_dir / 'train' / 'images'),  # 전체 경로 지정
            'val': str(self.output_dir / 'val' / 'images'),      # 전체 경로 지정
            'names': {i: name for i, name in enumerate(self.class_names)}
        }

        yaml_path = self.output_dir / 'dataset.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False)

        return str(yaml_path)  # yaml 파일의 경로 반환

class FoodDetector:
    def __init__(self, model_path=None):
        if model_path:
            self.model = YOLO(model_path)
        else:
            self.model = YOLO('yolov8x.pt')
    
    def train(self, data_yaml, epochs=100, batch_size=16, imgsz=320):
        print("Starting model training...")
        try:
            results = self.model.train(
                data=str(Path(data_yaml).absolute()),  # 절대 경로 사용
                epochs=epochs,
                imgsz=imgsz,
                batch=batch_size,
                patience=5,
                device=0,
                amp=True
            )
            return results
        except Exception as e:
            print(f"Training error: {e}")
            return None
        
    def detect_foods(self, image_path):
        results = self.model.predict(image_path)
        
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0]  # 바운딩 박스 좌표
                c = box.cls  # 클래스
                conf = box.conf  # 신뢰도
                detections.append({
                    'bbox': b.tolist(),
                    'class': c.item(),
                    'confidence': conf.item()
                })
        
        return detections

class NutritionAnalyzer:
    def __init__(self, nutrition_file):
        self.nutrition_data = self._load_nutrition_data(nutrition_file)
    
    def _load_nutrition_data(self, nutrition_file):
        try:
            df = pd.read_excel(nutrition_file)
            df = df.groupby('식품명').first().reset_index()
            return df.set_index('식품명').to_dict('index')
        except Exception as e:
            print(f"Error loading nutrition data: {e}")
            return {}
    
    def analyze_meal(self, detections, class_names):
        meal_analysis = {
            'dishes': [],
            'total_nutrition': {
                'calories': 0,
                'protein': 0,
                'fat': 0,
                'carbs': 0
            }
        }
        
        for det in detections:
            food_name = class_names[int(det['class'])]
            nutrition = self.nutrition_data.get(food_name, {})
            
            meal_analysis['dishes'].append({
                'name': food_name,
                'confidence': det['confidence'],
                'nutrition': nutrition
            })
            
            # 영양정보 합산
            for key in meal_analysis['total_nutrition']:
                meal_analysis['total_nutrition'][key] += nutrition.get(key, 0)
        
        return meal_analysis

import cv2
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
font_path = "C:/Windows/Fonts/malgun.ttf"  # Windows용
fontprop = fm.FontProperties(fname=font_path, size=12)
plt.rc('font', family=fontprop.get_name())

def plot_detections(image_path, detections, class_names):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(12, 8))
    plt.imshow(img)
    
    for det in detections:
        bbox = det['bbox']
        class_id = int(det['class'])
        conf = det['confidence']
        
        # 바운딩 박스 그리기
        plt.gca().add_patch(plt.Rectangle(
            (bbox[0], bbox[1]),
            bbox[2] - bbox[0],
            bbox[3] - bbox[1],
            fill=False,
            color='red',
            linewidth=2
        ))
        
        # 클래스명과 신뢰도 표시 (한글 정상 표시)
        plt.text(
            bbox[0],
            bbox[1] - 5,
            f'{class_names[class_id]} ({conf:.2f})',
            color='red',
            fontsize=10,
            fontproperties=fontprop,  # 한글 폰트 적용
            bbox=dict(facecolor='white', alpha=0.8)
        )
    
    plt.axis('off')
    plt.show()

def main():
    # 현재 작업 디렉토리의 절대 경로를 기준으로 설정
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "Food")
    OUTPUT_DIR = os.path.join(BASE_DIR, "yolo_dataset")
    NUTRITION_FILE = os.path.join(BASE_DIR, "FDDB.xlsx")
    
    # 1. 데이터셋 준비
    print("=== Preparing Dataset ===")
    preparator = DatasetPreparator(DATA_DIR, OUTPUT_DIR)
    preparator.prepare_yolo_dataset()
    
    # 2. 모델 학습
    print("\n=== Training Model ===")
    detector = FoodDetector()
    results = detector.train(
        str(Path(OUTPUT_DIR) / 'dataset.yaml'),
        epochs=1,
        batch_size=8,
        imgsz=320
    )
    
    # 3. 영양분석기 초기화
    analyzer = NutritionAnalyzer(NUTRITION_FILE)
    
    # 4. 테스트 (옵션)
    test_image = "test_meal.jpg"  # 테스트 이미지 경로
    if os.path.exists(test_image):
        print("\n=== Testing Model ===")
        # 음식 탐지
        detections = detector.detect_foods(test_image)
        
        # 결과 시각화
        plot_detections(test_image, detections, preparator.class_names)
        
        # 영양정보 분석
        meal_info = analyzer.analyze_meal(detections, preparator.class_names)
        
        print("\n=== Meal Analysis ===")
        print("\nDetected Dishes:")
        for dish in meal_info['dishes']:
            print(f"- {dish['name']} (confidence: {dish['confidence']:.2f})")
        
        print("\nTotal Nutrition:")
        for key, value in meal_info['total_nutrition'].items():
            print(f"- {key}: {value}")

if __name__ == "__main__":
    main()