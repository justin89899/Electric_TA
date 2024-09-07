import os
import pandas as pd
import fitz  # PyMuPDF for handling PDFs
from openai import OpenAI
from dotenv import load_dotenv
import dropbox
import numpy as np
import json

# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


# Find the most relevant slide for each answer
def find_relevant_slide(texts, answer_embedding):
    """Find the most relevant slide for the answer."""
    highest_similarity = -1
    most_relevant_slide_index = 0
    for index, slide_text in enumerate(texts):
        # Ensure each slide text is a single string
        slide_text_str = " ".join(slide_text.split("\n"))
        slide_embedding = get_embedding(slide_text_str)
        similarity = cosine_similarity(slide_embedding, answer_embedding)
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_relevant_slide_index = index
    return most_relevant_slide_index


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def pdf_to_text(pdf_path):
    """Converts PDF slides to text for each page."""
    doc = fitz.open(pdf_path)
    texts = [page.get_text() for page in doc]
    doc.close()
    return texts


def precalculate_embeddings_and_save(pdf_paths):
    all_embeddings = {}

    for pdf_path in pdf_paths:
        texts = pdf_to_text(pdf_path)
        embeddings = [get_embedding(text) for text in texts]
        all_embeddings[pdf_path] = embeddings

    with open('slides_embeddings.json', 'w') as f:
        # Convert the numpy arrays to list for JSON serialization
        json.dump({k: [emb.tolist() if isinstance(emb, np.ndarray) else emb for emb in v] for k, v in all_embeddings.items()}, f)


def load_precalculated_embeddings(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return {k: [np.array(emb) for emb in v] for k, v in data.items()}


def process_answers(precomputed_embeddings_path, answers):
    """Processes a list of answers and finds the most relevant slide using precalculated embeddings."""
    if not os.path.exists("slides_embeddings.json"):
        slides_pdf_folder = "Lectures/slides"
        pdf_paths = [os.path.join(slides_pdf_folder, f) for f in os.listdir(slides_pdf_folder) if f.endswith('.pdf')]
        precalculate_embeddings_and_save(pdf_paths)

    all_embeddings = load_precalculated_embeddings(precomputed_embeddings_path)
    most_relevant_slide_info = None
    highest_similarity = -1

    for answer in answers:
        answer_embedding = get_embedding(answer)  # You still need to embed the new answer

        for pdf_path, slide_embeddings in all_embeddings.items():
            for slide_index, slide_embedding in enumerate(slide_embeddings):
                similarity = cosine_similarity(slide_embedding, answer_embedding)

                if similarity > highest_similarity:
                    highest_similarity = similarity
                    most_relevant_slide_info = (pdf_path, slide_index)

    if most_relevant_slide_info:
        pdf_path, slide_index = most_relevant_slide_info
        output_path = os.path.join(
            "snapshots",
            f"{os.path.basename(pdf_path).split('.')[0]}_slide_{slide_index}.png"
        )
        capture_slide_as_image(pdf_path, slide_index, output_path)
        return output_path
    else:
        return "No slides found associated with the questions!"

# def process_answers(pdf_paths, answers):
#     """Processes a list of answers and finds the single most relevant slide across PDFs."""
#     most_relevant_slide_info = None
#     highest_similarity = -1
#
#     for answer in answers:
#         # Embed the answer only once
#         answer_embedding = get_embedding(answer)
#
#         # Search all PDFs for the most relevant slide to this answer
#         for pdf_path in pdf_paths:
#             texts = pdf_to_text(pdf_path)
#
#             for slide_index, slide_text in enumerate(texts):
#                 slide_embedding = get_embedding(slide_text)
#                 similarity = cosine_similarity(slide_embedding, answer_embedding)
#
#                 if similarity > highest_similarity:
#                     highest_similarity = similarity
#                     most_relevant_slide_info = (pdf_path, slide_index)
#
#         # After finding the most relevant slide, capture it as an image
#         if most_relevant_slide_info:
#             pdf_path, slide_index = most_relevant_slide_info
#             output_path = os.path.join(
#                 "snapshots",
#                 f"{os.path.basename(pdf_path).split('.')[0]}_slide_{slide_index}.png"
#             )
#             capture_slide_as_image(pdf_path, slide_index, output_path)
#             return output_path  # Return the path for further use
#         else:
#             return "No slides found associated with the questions!"


def capture_slide_as_image(pdf_path, slide_index, output_path):
    """Captures a specific slide as an image from a PDF."""
    # Ensure the directory where the snapshot will be saved exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = fitz.open(pdf_path)
    page = doc.load_page(slide_index)  # Load the page
    pix = page.get_pixmap()  # Get a pixmap (image) of the page
    pix.save(output_path)  # Save the pixmap as an image file
    doc.close()  # Close the document


def upload_to_dropbox(file_path, access_token):
    dbx = dropbox.Dropbox(access_token)
    with open(file_path, "rb") as f:
        file_name = os.path.basename(file_path)
        try:
            response = dbx.files_upload(f.read(), f"/{file_name}", mode=dropbox.files.WriteMode.overwrite)
            return response
        except dropbox.exceptions.ApiError as err:
            print(f"Failed to upload {file_path}: {err}")
            return None


def get_shareable_link(dbx, file_path):
    try:
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(file_path)
        return shared_link_metadata.url
    except dropbox.exceptions.ApiError as err:
        print(f"Failed to create shareable link for {file_path}: {err}")
        return None







