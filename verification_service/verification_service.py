import logging
from typing import Dict, Any
from .ocr_service import OcrService
from .img_similarity_service import ImgSimilarityService, SimilarityAnalysisDTO
from .reference_img_service import ReferenceImgService

logger = logging.getLogger(__name__)

class VerificationDTO:    
    def __init__(self, is_valid: bool, extracted_text: str, message: str, detail_message: str):
        self.is_valid = is_valid
        self.extracted_text = extracted_text
        self.message = message
        self.detail_message = detail_message
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "isValid": self.is_valid,
            "extractedText": self.extracted_text,
            "message": self.message,
            "detailMessage": self.detail_message
        }


"""수강생 인증 처리 서비스"""
class VerificationService:
    def __init__(self):
        self.OCR_WEIGHT = 0.7
        self.SIMILARITY_WEIGHT = 0.3
        self.PASS_THRESHOLD = 0.65
        
        self.reference_img_service = ReferenceImgService()
        self.ocr_service = OcrService()
        self.img_similarity_service = ImgSimilarityService(self.reference_img_service)
    
    def verify_student(self, image_bytes: bytes, filename: str = None) -> VerificationDTO:
        try:
            similarity_analysis = self.img_similarity_service.analyze_similarity(image_bytes)
            
            if not similarity_analysis.is_layout_similar:
                logger.info(f"레이아웃 유사도가 낮아 OCR 진행 하지 않음. 최고 유사도: {similarity_analysis.max_similarity:.2f}")
                return VerificationDTO(
                    is_valid=False,
                    extracted_text="",
                    message="인증 실패",
                    detail_message=f"프로그래머스 정식 레이아웃과 유사도가 낮습니다."
                )

            extracted_text = self.ocr_service.extract_text(image_bytes, filename)
            ocr_score = self._calculate_ocr_score(extracted_text)
            similarity_score = similarity_analysis.similarity_score
            
            final_score = (ocr_score * self.OCR_WEIGHT) + (similarity_score * self.SIMILARITY_WEIGHT)
            is_valid = final_score >= self.PASS_THRESHOLD
            
            detail_message = self._generate_detail_message(
                ocr_score, similarity_score, final_score, similarity_analysis
            )
            
            return VerificationDTO(
                is_valid=is_valid,
                extracted_text=extracted_text,
                message="데브코스 수강생 인증 성공!" if is_valid else "인증 실패",
                detail_message=detail_message
            )
            
        except Exception as e:
            logger.error("인증 처리 실패", exc_info=True)
            return VerificationDTO(
                is_valid=False,
                extracted_text="",
                message=f"이미지 처리 중 오류 발생: {str(e)}",
                detail_message=""
            )
    
    def _calculate_ocr_score(self, text: str) -> float:
        """OCR 텍스트에서 점수를 계산합니다."""
        if not text or not text.strip():
            return 0.0
        
        lower_text = text.lower().replace(" ", "")
        
        has_kdt = "kdt" in lower_text
        has_devcourse = "데브코스" in lower_text
        
        score = 0.0
        if has_kdt:
            score += 0.7
        if has_devcourse:
            score += 0.3
        
        logger.info(f"OCR 점수: {score} (KDT: {has_kdt}, 데브코스: {has_devcourse}, 텍스트: {lower_text[:50]}...)")
        return score
    
    def _generate_detail_message(self, ocr_score: float, similarity_score: float, 
                                final_score: float, analysis: SimilarityAnalysisDTO) -> str:
        """상세 분석 메시지를 생성합니다."""
        message = []
        message.append(f"OCR 점수: {ocr_score:.2f} (키워드 매칭)")
        message.append(f"유사도 점수: {similarity_score:.2f} (레이아웃 분석)")
        message.append(f"최고 유사도: {analysis.max_similarity:.2f}")
        message.append(f"최종 점수: {final_score:.2f}")
        
        if not analysis.is_layout_similar:
            message.append("프로그래머스 정식 레이아웃과 유사도가 낮습니다.")
        
        return "\n".join(message) 