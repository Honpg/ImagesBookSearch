import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from mongo_client import CustomMongoClient
from triton_client import TritonClient
import os

class BookSearch:
    def __init__(self, model=TritonClient, db_name="book_search"):
        self.model = model
        self.mongo_client = CustomMongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client.get_db(db_name)
        self.books_collection = self.db['books']

        self.books_collection.create_index([("title", "text")])

    def search_books_by_title(self, title_query, limit=10):
        """Tìm kiếm sách theo tiêu đề."""
        books = self.books_collection.find(
            {"$text": {"$search": title_query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)

        results = [
            {
                "title": book["title"],
                "price": book.get("price", ""),
                "score": book.get("score", 0),
                "encoded_image": book.get["encoded_image"]
            } for book in books
        ]
        return results

    def search_books_by_image_embedding(self, input_embedding, limit=10):
        """Tìm kiếm sách theo image embedding."""
        books = self.books_collection.find({"image_embedding": {"$exists": True}}).limit(limit)

        results = []
        for book in books:
            book_embedding = np.array(book["image_embedding"])
            similarity_score = self.calculate_similarity(input_embedding, book_embedding)
            results.append({
                "title": book["title"],
                "price": book.get("price", ""),
                "image_similarity_score": similarity_score,
                "encoded_image": book.get["encoded_image"]
            })

        return sorted(results, key=lambda x: x["image_similarity_score"], reverse=True)

    def calculate_similarity(self, emb1, emb2):
        """Tính toán độ tương đồng cosine."""
        return cosine_similarity([emb1], [emb2])[0][0]
