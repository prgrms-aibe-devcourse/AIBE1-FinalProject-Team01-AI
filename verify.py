import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verification_service.app import app, initialize_services

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        initialize_services()
        
        # Flask 앱 실행
        app.run(
            host=os.getenv('FLASK_HOST'),
            port=int(os.getenv('FLASK_PORT')),
            debug=False
        )
    except Exception as e:
        logging.error("서비스 시작 실패", exc_info=True)
        sys.exit(1) 