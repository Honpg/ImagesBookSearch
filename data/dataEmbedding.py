import pandas as pd
from PIL import Image
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import numpy as np
from sentence_transformers import SentenceTransformer


# Embedding class to generate embeddings for text and images
class Embedding:
    def __init__(self, df: pd.DataFrame = None, image_path: str = None):
        # Initialize with a DataFrame for text or an image path for image embeddings
        if df is not None:
            self.df = df  # Store the DataFrame
        else:
            self.df = None

        if image_path:
            try:
                # Load and convert the image to RGB
                self.image = Image.open(image_path).convert("RGB")
            except Exception as e:
                raise ValueError(f"Error loading image from {image_path}: {e}")
        else:
            self.image = None

        # Load a pre-trained ResNet-50 model for image feature extraction
        self.modelImg = models.resnet50(pretrained=True)
        # Remove the classification layer to use as a feature extractor
        self.modelImg = torch.nn.Sequential(*list(self.modelImg.children())[:-1])
        self.modelImg.eval()  # Set model to evaluation mode

        # Load a pre-trained SentenceTransformer model for text embeddings
        self.modelText = SentenceTransformer("paraphrase-MiniLM-L6-v2")

    # Function to create text embeddings
    def Text_embedding(self, column: str) -> np.ndarray:
        # Check if the DataFrame and the specified column are valid
        if self.df is None or column not in self.df:
            raise ValueError(f"Invalid DataFrame or column: {column}")

        # Generate embeddings for the text in the specified column
        embedding = self.modelText.encode(self.df[column])
        return embedding

    # Function to preprocess images before embedding
    def Image_preprocessing(self) -> torch.Tensor:
        if self.image is None:
            raise ValueError("Image not loaded.")

        # Define preprocessing steps: resizing, cropping, normalizing, and converting to a tensor
        preprocess = transforms.Compose(
            [
                transforms.Resize(256),  # Resize the image to 256 pixels on the shorter side
                transforms.CenterCrop(224),  # Crop the center to 224x224 pixels
                transforms.ToTensor(),  # Convert the image to a tensor
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalize
            ]
        )

        # Apply preprocessing and add a batch dimension
        return preprocess(self.image).unsqueeze(0)

    # Function to create image embeddings
    def Image_embedding(self) -> np.ndarray:
        # Preprocess the image
        image = self.Image_preprocessing()
        with torch.no_grad():  # Disable gradient computation
            # Pass the image through the model to extract features
            features = self.modelImg(image)
        # Convert the features to a NumPy array and remove the singleton dimensions
        return features.squeeze().numpy()
