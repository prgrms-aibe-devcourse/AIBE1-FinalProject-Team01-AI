from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging
import os
import json
from dotenv import load_dotenv
from .verification_service import VerificationService

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)  

verification_service = None

def initialize_services():
    global verification_service
    try:
        verification_service = VerificationService()
        logging.info("인증 서비스 초기화 완료")
    except Exception as e:
        logging.error("서비스 초기화 실패", exc_info=True)
        raise


"""수강생 인증 서비스"""
@app.route('/verify', methods=['POST'])
def verify_student():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "이미지 파일이 없습니다"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "선택된 파일이 없습니다"}), 400
        
        image_bytes = file.read()
        result = verification_service.verify_student(image_bytes, file.filename)
        return Response(
            json.dumps({
                "success": True,
                "data": result.to_dict()
            }, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        logging.error("인증 API 처리 실패", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"서버 오류: {str(e)}"
        }), 500


""" [dev] OCR 분석 """
@app.route('/verify/ocr', methods=['POST'])
def extract_text_only():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "이미지 파일이 없습니다"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "선택된 파일이 없습니다"}), 400
        
        image_bytes = file.read()
        extracted_text = verification_service.ocr_service.extract_text(image_bytes)
        
        return Response(
            json.dumps({
                "success": True,
                "data": {
                    "extractedText": extracted_text
                }
            }, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        logging.error("OCR API 처리 실패", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"서버 오류: {str(e)}"
        }), 500



""" [dev] 이미지 유사도 분석 """
@app.route('/verify/similarity', methods=['POST'])
def analyze_similarity_only():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "이미지 파일이 없습니다"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "선택된 파일이 없습니다"}), 400

        image_bytes = file.read()
        analysis = verification_service.img_similarity_service.analyze_similarity(image_bytes)
        
        return Response(
            json.dumps({
                "success": True,
                "data": {
                    "maxSimilarity": analysis.max_similarity,
                    "avgSimilarity": analysis.avg_similarity,
                    "similarityScore": analysis.similarity_score,
                    "similarities": analysis.similarities,
                    "isLayoutSimilar": analysis.is_layout_similar
                }
            }, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        logging.error("유사도 분석 API 처리 실패", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"서버 오류: {str(e)}"
        }), 500


if __name__ == '__main__':
    initialize_services()
    host = os.getenv('FLASK_HOST')
    port = int(os.getenv('FLASK_PORT'))
    
    logging.info(f"Flask 서버 시작: {host}:{port}")
    app.run(host=host, port=port, debug=False) 