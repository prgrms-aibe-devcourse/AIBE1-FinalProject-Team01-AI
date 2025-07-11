import os
import logging
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)

"""기준 이미지 분석 서비스"""
class ReferenceImgService:
    
    def __init__(self, reference_dir: str = "reference_images"):
        self.reference_images: List[bytes] = []
        self.reference_dir = reference_dir
        self.load_reference_images()
    
    def load_reference_images(self):
        self.reference_images = []
        
        reference_files = [
            "data1.jpg",
            "data2.jpg", 
            "data3.jpg",
            "data5.png",
            "data6.png"
        ]
        
        for file_name in reference_files:
            try:
                file_path = Path(self.reference_dir) / file_name
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        image_bytes = f.read()
                        self.reference_images.append(image_bytes)
                        logger.info(f"참조 이미지 로드 완료: {file_name}")
                else:
                    logger.warning(f"참조 이미지 없음: {file_name}")
            except Exception as e:
                logger.warning(f"참조 이미지 로드 실패: {file_name}", exc_info=True)
        
        logger.info(f"총 {len(self.reference_images)}개의 참조 이미지 로드 완료")
    
    def get_reference_images(self) -> List[bytes]:
        return self.reference_images 