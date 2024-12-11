from pymongo import MongoClient

class CustomMongoClient:
    def __init__(self, url):
        self.client = MongoClient(url)  
        self.db = None

    def get_db(self, db_name="default_db"):
        """Lấy đối tượng db từ MongoClient."""
        if self.db is None:
            self.db = self.client[db_name]
        return self.db
