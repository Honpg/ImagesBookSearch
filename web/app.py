from flask import Flask, request, jsonify, render_template
from web.book_search import BookSearch
from web.triton_client import TritonClient
from web.mongo_client import CustomMongoClient
import os
from PIL import Image
from torchvision import transforms

app = Flask(__name__)

TEMP_IMAGE_FOLDER = "temp_images"
os.makedirs(TEMP_IMAGE_FOLDER, exist_ok=True)

try:
    mongo_client = CustomMongoClient(os.getenv('MONGO_URL'))
    db = mongo_client.get_db()
    print("Kết nối MongoDB thành công!")
except Exception as e:
    print(f"Lỗi khi kết nối MongoDB: {e}")

triton_client = TritonClient(server_url="http://triton-server:8000")

book_search = BookSearch(model=triton_client)

@app.route("/")
def home():
    """Serve the HTML frontend."""
    return render_template('frontend.html')

@app.route("/reset", methods=["POST"])
def reset_state():
    """Reset server state."""
    for file_name in os.listdir(TEMP_IMAGE_FOLDER):
        os.remove(os.path.join(TEMP_IMAGE_FOLDER, file_name))
    return jsonify({"message": "Reset completed"}), 200

@app.route("/search/title", methods=["POST"])
def search_by_title():
    """Search books by title."""
    title = request.form.get("title")
    if not title:
        return jsonify({"error": "Title is required"}), 400
    results = book_search.search_books_by_title(title)
    return jsonify({"results": results})

@app.route("/search/image", methods=["POST"])
def search_by_image():
    """Search books by image."""
    image_file = request.files.get("image")
    if not image_file:
        return jsonify({"error": "Image is required"}), 400

    image = Image.open(image_file)
    preprocess = transforms.Compose([
    transforms.Resize((256, 256)),  
    transforms.ToTensor(),  
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  
])
    image_tensor = preprocess(image).unsqueeze(0)  
    image_array = image_tensor.detach().numpy() 

    try:
        result = triton_client.call_triton_inference("resnet50", image_array)
        results = book_search.search_books_by_image_embedding(result)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500