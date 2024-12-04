from dataEmbedding import Embedding
import os
import pandas as pd
import numpy as np

# Function to calculate text embeddings
def textVec(df, column):
    # Check if the column exists in the DataFrame
    if column not in df.columns:
        print(f"Available columns: {df.columns}")  # Debugging message
        raise ValueError(f"Invalid DataFrame or column: {column}")
    emb = Embedding(df)
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

# Function to update a CSV file with embedding data
def csvUpdate(df, nameVec, imageVecs, output_csv_path):
    # Add the text and image embeddings to the DataFrame
    df['nameVec'] = [vec.tolist() for vec in nameVec]
    df['imageVec'] = [
        vec.tolist() if isinstance(vec, np.ndarray) else vec
        for vec in imageVecs
    ]

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False, encoding='UTF-8')

# Main script execution
if __name__ == "__main__":
    # Path to the input CSV file
    csv_path = 'D:/study/OJT/project/data/spibook/spibook/output.csv'
    output_csv_path = 'D:/study/OJT/project/data/spibook/spibook/output_with_embeddings.csv'

    # Load the input CSV data
    df = pd.read_csv(csv_path)

    # Generate text embeddings for the 'name' column
    nameVec = textVec(df, 'title')

    # Generate image embeddings for each item's image path
    imageVecs = []
    for _, row in df.iterrows():  # Iterate through each row in the DataFrame
        image_path = row['image path']  # Get the image path from the row
        imageVecs.append(imgVec(image_path))  # Append the image embedding to the list

    # Update the CSV file with the generated embeddings
    csvUpdate(df, nameVec, imageVecs, output_csv_path)
