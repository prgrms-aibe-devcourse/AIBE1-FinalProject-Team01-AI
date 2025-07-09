import requests
import uuid
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_url = os.getenv('OCR_API_URL')
secret_key = os.getenv('OCR_SECRET_KEY')
image_file = os.getenv('IMAGE_FILE')

if not api_url or not secret_key or not image_file:
    print("Error: 환경변수가 설정되지 않았습니다.")
    print("OCR_API_URL, OCR_SECRET_KEY, IMAGE_FILE을 .env 파일에 설정해주세요.")
    exit()

if not os.path.exists(image_file):
    print(f"Error: {image_file} 파일을 찾을 수 없습니다.")
    exit()

try:
    request_json = {
        'images': [
            {
                'format': 'jpg',
                'name': 'data1'
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [
      ('file', open(image_file,'rb'))
    ]
    headers = {
      'X-OCR-SECRET': secret_key
    }

    response = requests.request("POST", api_url, headers=headers, data=payload, files=files)

    if response.status_code != 200:
        print(f"API 요청 실패: {response.status_code}")
        print(f"응답 내용: {response.text}")
        exit()
    
    result = response.json()
    
    if 'error' in result:
        print(f"OCR API 에러: {result['error']}")
        exit()

    def extract_infer_texts(obj):
        texts = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'inferText' and isinstance(v, str):
                    texts.append(v)
                else:
                    texts.extend(extract_infer_texts(v))
        elif isinstance(obj, list):
            for item in obj:
                texts.extend(extract_infer_texts(item))
        return texts

    all_texts = extract_infer_texts(result)
    
    print("=== 추출된 텍스트 ===")
    print(' '.join(all_texts))

    keywords = ["KDT", "데브코스"]
    verification = 0

    print("=== 키워드 검증 과정 ===")
    for keyword in keywords:
        count = 0
        for text in all_texts:
            if keyword in text:
                verification += 1
                count += 1
        print(f"'{keyword}' 키워드: {count}회 발견")

    print(f"최종 검증 점수: {verification}")

except requests.exceptions.RequestException as e:
    print(f"네트워크 오류: {e}")
except json.JSONDecodeError as e:
    print(f"JSON 파싱 오류: {e}")
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()