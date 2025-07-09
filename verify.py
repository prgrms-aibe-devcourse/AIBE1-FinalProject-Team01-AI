from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import torch
from torchvision import transforms
from transformers import CLIPProcessor, CLIPModel
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)  # CORS 허용 (Spring Boot 연동을 위해)

# 전역 변수: 모델, 프로세서, 기준 이미지 임베딩
model = None
processor = None
reference_embedding = None
THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.85'))  # 환경변수에서 임계값 가져오기

# 이미지 전처리 및 임베딩 추출 함수
def get_image_embedding(image: Image.Image):
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model.get_image_features(**inputs)
        normalized = outputs / outputs.norm(dim=-1, keepdim=True)
    return normalized

# 서버 시작 시 모델 및 기준 이미지 로딩
def load_model_and_reference():
    global model, processor, reference_embedding

    print("모델과 기준 이미지 로딩 중...")

    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    # 기준 이미지 경로 (환경변수에서 가져오기)
    reference_path = os.getenv('IMAGE_FILE', 'assets/data1.jpg')
    if not os.path.exists(reference_path):
        raise FileNotFoundError(f"기준 이미지가 {reference_path}에 없습니다.")

    ref_image = Image.open(reference_path).convert("RGB")
    reference_embedding = get_image_embedding(ref_image)

    print("기준 이미지 임베딩 완료.")

# 인증 API 엔드포인트
@app.route('/verify', methods=['POST'])
def verify():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    image = Image.open(file).convert("RGB")

    # 입력 이미지 임베딩
    input_embedding = get_image_embedding(image)

    # Cosine Similarity 계산
    score = torch.nn.functional.cosine_similarity(reference_embedding, input_embedding).item()
    is_similar = score >= THRESHOLD

    return jsonify({
        "score": round(score, 4),
        "isSimilar": is_similar
    })

# 서버 실행
if __name__ == '__main__':
    # 서버 시작 전에 모델과 기준 이미지 로딩
    load_model_and_reference()
    
    # 환경변수에서 호스트와 포트 가져오기
    host = os.getenv('FLASK_HOST')
    port = int(os.getenv('FLASK_PORT'))
    
    app.run(host=host, port=port)