import requests
import uuid
import time
import json
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

"""OCR 서비스스"""
class OcrService:
    def __init__(self):
        load_dotenv()
        self.api_url = os.getenv('OCR_API_URL')
        self.secret_key = os.getenv('OCR_SECRET_KEY')
        
        if not self.api_url or not self.secret_key:
            logger.warning("OCR API 설정 실패")
    
    def extract_text(self, image_bytes: bytes, filename: str = None) -> str:
        try:
            if not self.api_url or not self.secret_key:
                logger.error("OCR API 설정 실패")
                return ""
            
            if filename:
                file_extension = filename.split('.')[-1].lower() if '.' in filename else 'jpg'
                original_filename = filename
            else:
                file_extension = 'jpg'
                original_filename = 'image.jpg'

            request_json = {
                'images': [
                    {
                        'format': file_extension,
                        'name': original_filename
                    }
                ],
                'requestId': str(uuid.uuid4()),
                'version': 'V2',
                'timestamp': int(round(time.time() * 1000))
            }

            payload = {'message': json.dumps(request_json).encode('UTF-8')}
            files = [('file', (original_filename, image_bytes, f'image/{file_extension}'))]
            headers = {'X-OCR-SECRET': self.secret_key}

            response = requests.post(self.api_url, headers=headers, data=payload, files=files)

            if response.status_code != 200:
                logger.error(f"OCR API 요청 실패: {response.status_code}")
                return ""

            result = response.json()
            
            if 'error' in result:
                logger.error(f"OCR API 에러: {result['error']}")
                return ""

            all_texts = self._extract_infer_texts(result)
            extracted_text = ' '.join(all_texts)
            
            logger.info(f"OCR 텍스트 추출 완료: {extracted_text[:100]}...")
            return extracted_text

        except Exception as e:
            logger.error("OCR 텍스트 추출 실패", exc_info=True)
            return ""
    
    def _extract_infer_texts(self, obj) -> list:
        texts = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'inferText' and isinstance(v, str):
                    texts.append(v)
                else:
                    texts.extend(self._extract_infer_texts(v))
        elif isinstance(obj, list):
            for item in obj:
                texts.extend(self._extract_infer_texts(item))
        return texts 