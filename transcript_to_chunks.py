from PyPDF2 import PdfReader
import os
import re
import pandas as pd
from langchain.text_splitter import CharacterTextSplitter

def get_pdf_text(pdf_path):
    with open(pdf_path, 'rb') as f:
        print(pdf_path)
        pdf_reader = PdfReader(f)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text


def get_text_chunks(text, chunk_size=500, chunk_overlap=100):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return text_splitter.split_text(text)


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def pdf_to_text_chunks(file_name):
    path = 'documents'
    all_chunks = []  # List to store all chunks from all lectures
    chunk_indices = []  # List to store indices of chunks

    pdf_files = sorted([f for f in os.listdir(path) if f.endswith('.pdf')], key=natural_keys)
    for lecture_number, pdf_file in enumerate(pdf_files, start=1):
        pdf_path = os.path.join(path, pdf_file)
        text = get_pdf_text(pdf_path)

        chunks = get_text_chunks(text)
        for chunk_number, chunk in enumerate(chunks, start=1):
            all_chunks.append(chunk)
            chunk_indices.append(f"Lecture{lecture_number}_Chunk{chunk_number}")

    # Create DataFrame and save to CSV
    df = pd.DataFrame({'Index': chunk_indices, 'Text': all_chunks})
    df.to_csv(file_name, index=False)


# pdf_to_text_chunks('text_chunks.csv')
