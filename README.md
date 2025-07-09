# AI-Test - 수강생 인증 서비스

자바 백엔드의 verification 서비스와 동일한 기능을 제공하는 파이썬 기반 인증 서비스입니다.

## 기능

- **레이아웃 유사도 분석**: CLIP 모델을 사용한 레이아웃 검사 (우선 수행)
- **OCR 서비스**: 이미지에서 텍스트 추출 (KDT, 데브코스 키워드 검증)
- **참조 이미지 관리**: 프로그래머스 정식 레이아웃 이미지들과 비교
- **통합 인증**: 레이아웃 검사 후 OCR을 결합한 최종 인증 판정

## 구조

```
Ai-Test/
├── verification_service/          # 통합 서비스
│   ├── __init__.py
│   ├── reference_img_service.py   # 참조 이미지 관리
│   ├── ocr_service.py            # OCR 텍스트 추출
│   ├── img_similarity_service.py # 이미지 유사도 분석
│   ├── verification_service.py   # 메인 인증 서비스
│   └── app.py                    # Flask 서버
├── ocr.py                        # 기존 OCR 스크립트
├── verify.py                     # 서비스 실행 스크립트
├── requirements.txt
└── reference_images/             # 참조 이미지 폴더
    ├── data1.jpg
    ├── data2.jpg
    ├── data3.jpg
    ├── data5.png
    └── data6.png
```

## 설치 및 실행

1. **의존성 설치**

```bash
pip install -r requirements.txt
```

2. **환경변수 설정**
   `.env` 파일을 생성하고 다음 변수들을 설정하세요:

```
OCR_API_URL=your_ocr_api_url
OCR_SECRET_KEY=your_ocr_secret_key
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

3. **참조 이미지 준비**
   `reference_images/` 폴더에 다음 이미지들을 배치하세요:

- data1.jpg
- data2.jpg
- data3.jpg
- data5.png
- data6.png

4. **서비스 실행**

```bash
python verify.py
```

## API 엔드포인트

### 1. 전체 인증 (`POST /verify`)

OCR과 이미지 유사도를 모두 분석하여 최종 인증 결과를 반환합니다.

**요청:**

- `image`: 이미지 파일 (multipart/form-data)

**응답:**

```json
{
  "success": true,
  "data": {
    "isValid": true,
    "extractedText": "추출된 텍스트",
    "message": "데브코스 수강생 인증 성공!",
    "detailMessage": "OCR 점수: 0.70 (키워드 매칭)\n유사도 점수: 0.85 (레이아웃 분석)\n최고 유사도: 0.92\n최종 점수: 0.75"
  }
}
```

### 2. OCR만 수행 (`POST /verify/ocr`)

이미지에서 텍스트만 추출합니다.

### 3. 유사도만 분석 (`POST /verify/similarity`)

이미지 유사도만 분석합니다.

### 4. 레이아웃이 낮은 경우 응답

레이아웃 유사도가 0.7 미만인 경우 OCR을 건너뛰고 즉시 실패를 반환합니다.

```json
{
  "success": true,
  "data": {
    "isValid": false,
    "extractedText": "",
    "message": "인증 실패",
    "detailMessage": "프로그래머스 정식 레이아웃과 유사도가 낮습니다.\n최고 유사도: 0.45"
  }
}
```

## 인증 프로세스

1. **레이아웃 검사**: CLIP 모델로 참조 이미지들과 유사도 분석
2. **임계값 판정**: 최고 유사도가 0.7 미만이면 즉시 실패
3. **OCR 수행**: 레이아웃이 충분한 경우에만 OCR 실행
4. **최종 판정**: OCR 점수(70%) + 유사도 점수(30%)로 최종 결정

## Spring Boot 연동

이 파이썬 서비스는 Spring Boot 백엔드와 연동할 수 있도록 설계되었습니다.
Spring Boot에서는 HTTP 클라이언트를 통해 이 Flask 서비스의 API를 호출하여 인증 기능을 수행할 수 있습니다.

### 테스트 방법

```bash
# 전체 인증 테스트
curl -X POST http://localhost:5000/verify \
  -F "image=@your_image.jpg"

# OCR만 테스트
curl -X POST http://localhost:5000/verify/ocr \
  -F "image=@your_image.jpg"

# 유사도만 테스트
curl -X POST http://localhost:5000/verify/similarity \
  -F "image=@your_image.jpg"
```
