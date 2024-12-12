from pymongo import MongoClient   
import os

class CustomMongoClient:
    def __init__(self, url):
        url = os.getenv('MONGO_URL')
        if not url:
            raise ValueError("Biến môi trường 'MONGO_URL' chưa được cấu hình!")
        
        try:
            self.client = MongoClient(url)
        except Exception as e:
            raise ConnectionError(f"Lỗi kết nối tới MongoDB: {str(e)}")
        self.db = None

    def get_db(self, db_name="default_db"):
        """Lấy đối tượng db từ MongoClient."""
        if self.db is None:
            self.db = self.client[db_name]
        return self.db
