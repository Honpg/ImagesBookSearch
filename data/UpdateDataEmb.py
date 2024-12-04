from dataEmbedding import Embedding
import json
import numpy as np
import pandas as pd
import os

# Function to calculate text embeddings
def textVec(df, column):
     # Create an instance of the Embedding class using the DataFrame
     emb = Embedding(df)
     # Generate embeddings for the specified column
     vec = emb.Text_embedding(column)
     return vec

# Function to calculate image embeddings
def imgVec(image_path):
     # Check if the file exists before processing
     if os.path.exists(image_path):  # Ensure the file path is valid and exists
          emb = Embedding(image_path=image_path)
          # Generate embeddings for the image
          vec = emb.Image_embedding()
          return vec
     else:
          # Handle missing image files by returning None
          return None

# Function to update a JSON file with embedding data
def jsonUpdate(data, nameVec, authorVec, imageVec, json_path):
     # Define the output JSON file path
     updated_json_path = os.path.join(os.path.dirname(json_path), 'output1.json')

     # Create an empty JSON file if it doesn't already exist
     if not os.path.exists(updated_json_path):
          with open(updated_json_path, 'w', encoding='UTF-8') as file:
               json.dump([], file, ensure_ascii=False, indent=4)

     # Update the vectors in each item of the data
     valid_data = []  # Initialize a list to hold valid data entries
     for i, item in enumerate(data):
          # Only include entries with valid image embeddings
          if imageVec[i] is not None:
               # Add the text and image embeddings to the current item
               item['nameVec'] = nameVec[i].tolist()
               item['authorVec'] = authorVec[i].tolist()
               item['imageVec'] = imageVec[i].tolist() if isinstance(imageVec[i], np.ndarray) else imageVec[i]
               valid_data.append(item)  # Add the updated item to the valid data list

     # Write the updated data to the output JSON file
     with open(updated_json_path, 'w', encoding='UTF-8') as file:
          json.dump(valid_data, file, ensure_ascii=False, indent=4)

# Main script execution
if __name__ == "__main__":
     # Path to the input JSON file
     json_path = 'D:/study/OJT/project/data/spibook/spibook/output.json'

     # Load the input JSON data
     with open(json_path, 'r', encoding='UTF-8') as file:
          data = json.load(file)

     # Convert the JSON data into a Pandas DataFrame
     df = pd.DataFrame(data)

     # Generate text embeddings for the 'name' and 'author' columns
     nameVec = textVec(df, 'name')
     authorVec = textVec(df, 'author')

     # Generate image embeddings for each item's image path
     imageVecs = []
     for item in data:  # Iterate through each item in the JSON data
          image_path = item['image_local_path']  # Get the image path from the item
          imageVecs.append(imgVec(image_path))  # Append the image embedding to the list

     # Update the JSON file with the generated embeddings
     jsonUpdate(data, nameVec, authorVec, imageVecs, json_path)
