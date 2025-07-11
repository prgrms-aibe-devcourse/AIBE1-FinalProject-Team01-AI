import os
import logging
from typing import List, Dict, Any
import torch
from torchvision import transforms
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import io
import numpy as np
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class SimilarityAnalysisDTO:    
    def __init__(self, max_similarity: float, avg_similarity: float, 
                 similarity_score: float, similarities: List[float], is_layout_similar: bool):
        self.max_similarity = max_similarity
        self.avg_similarity = avg_similarity
        self.similarity_score = similarity_score
        self.similarities = similarities
        self.is_layout_similar = is_layout_similar

class ImgSimilarityService:
    def __init__(self, reference_img_service):
        load_dotenv()
        self.reference_img_service = reference_img_service
        self.model = None
        self.processor = None
        self._load_model()
    
    def _load_model(self):
        try:
            logger.info("CLIP 모델 로딩 중...")
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            logger.info("CLIP 모델 로딩 완료")
        except Exception as e:
            logger.error("CLIP 모델 로딩 실패", exc_info=True)
            raise
    
    def analyze_similarity(self, image_bytes: bytes) -> SimilarityAnalysisDTO:
        try:
            logger.info(f"사용자 이미지 바이트 배열 받음: {len(image_bytes)} bytes")
            
            user_embedding = self._extract_image_embedding(image_bytes)
            
            similarities = []
            reference_images = self.reference_img_service.get_reference_images()
            logger.info(f"참조 이미지 개수: {len(reference_images)}")
            
            for i, reference_image in enumerate(reference_images):
                ref_embedding = self._extract_image_embedding(reference_image)
                similarity = self._calculate_cosine_similarity(user_embedding, ref_embedding)
                
                logger.info(f"참조 이미지 {i+1} 유사도: {similarity:.4f}")
                similarities.append(similarity)
            
            max_similarity = max(similarities) if similarities else 0.0
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
            similarity_score = self._calculate_similarity_score(max_similarity, avg_similarity)
            
            LAYOUT_THRESHOLD = 0.7
            
            return SimilarityAnalysisDTO(
                max_similarity=max_similarity,
                avg_similarity=avg_similarity,
                similarity_score=similarity_score,
                similarities=similarities,
                is_layout_similar=max_similarity > LAYOUT_THRESHOLD
            )
            
        except Exception as e:
            logger.error("유사도 분석 실패", exc_info=True)
            return self._create_error_result()
    
    """임베딩 추출"""
    def _extract_image_embedding(self, image_bytes: bytes) -> torch.Tensor:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            inputs = self.processor(images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model.get_image_features(**inputs)
                normalized = outputs / outputs.norm(dim=-1, keepdim=True)
            
            return normalized
            
        except Exception as e:
            logger.error("이미지 임베딩 추출 실패", exc_info=True)
            return torch.zeros(1, 512)
    
    def _calculate_cosine_similarity(self, embedding1: torch.Tensor, embedding2: torch.Tensor) -> float:
        try:
            similarity = torch.nn.functional.cosine_similarity(embedding1, embedding2).item()
            return similarity
        except Exception as e:
            logger.error("코사인 유사도 계산 실패", exc_info=True)
            return 0.0
    
    def _calculate_similarity_score(self, max_similarity: float, avg_similarity: float) -> float:
        return (max_similarity * 0.7) + (avg_similarity * 0.3)
    
    def _create_error_result(self) -> SimilarityAnalysisDTO:
        return SimilarityAnalysisDTO(
            max_similarity=0.0,
            avg_similarity=0.0,
            similarity_score=0.0,
            similarities=[],
            is_layout_similar=False
        ) 