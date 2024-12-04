import pandas as pd
from PIL import Image
import torch
from torchvision import models
from torchvision.models import ResNet50_Weights
import torchvision.transforms as transforms
import numpy as np
from sentence_transformers import SentenceTransformer


class Embedding:
    def __init__(self, df: pd.DataFrame = None, image_path: str = None):
        # Initialize with a DataFrame for text or an image path for image embeddings
        self.df = df if df is not None else None
        self.image = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # Support GPU if available

        if image_path:
            try:
                # Load and convert the image to RGB
                self.image = Image.open(image_path).convert("RGB")
            except Exception as e:
                raise ValueError(f"Error loading image from {image_path}: {e}")

        # Load pre-trained ResNet-50 for image feature extraction
        self.modelImg = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        self.modelImg = torch.nn.Sequential(*list(self.modelImg.children())[:-1])  # Remove classification layer
        self.modelImg = self.modelImg.to(self.device).eval()  # Move to device and set to eval mode

        # Load pre-trained SentenceTransformer for text embeddings
        self.modelText = SentenceTransformer("C:/Users/dodof/.cache/huggingface/hub/models--sentence-transformers--paraphrase-MiniLM-L6-v2/snapshots/9a27583f9c2cc7c03a95c08c5f087318109e2613")

    def Text_embedding(self, column: str) -> np.ndarray:
        if self.df is None or column not in self.df:
            raise ValueError(f"Invalid DataFrame or column: {column}")

        # Generate embeddings for text in the specified column
        return self.modelText.encode(self.df[column].tolist())

    def Image_preprocessing(self) -> torch.Tensor:
        if self.image is None:
            raise ValueError("Image not loaded.")

        preprocess = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

        return preprocess(self.image).unsqueeze(0).to(self.device)

    def Image_embedding(self) -> np.ndarray:
        image = self.Image_preprocessing()
        with torch.no_grad():
            features = self.modelImg(image)
        return features.squeeze().detach().cpu().numpy()
