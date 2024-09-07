from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# load text chunks from text_chunks.csv
def load_text_chunks(file_name):
    text_chunks = pd.read_csv(file_name)['Text']
    return text_chunks.to_list()

def save_vectorstore_to_json(file_path):


    text_chunks = load_text_chunks(file_path)
    vectorstore = get_vectorstore(text_chunks)
    vectorstore.save_local("text_chunks_faiss_index")
    

save_vectorstore_to_json('text_chunks.csv')