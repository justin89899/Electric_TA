from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import os

# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def get_all():
    # Replace 'text_chunk.csv' with the path to your CSV file
    file_path = 'text_chunks.csv'

    # Reading the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Suppose we want to calculate a new value based on columns 'A' and 'B'
    # For example, let's say the new column is the sum of 'A' and 'B'
    df['embedding'] = df.apply(lambda row: get_embedding(row['Text']) , axis=1)

    # Now, save the modified DataFrame back to a new CSV file
    df.to_csv('text_chunks_with_embedding.csv', index=False)
    print("Finish embedding, saved to csv.")
get_all()