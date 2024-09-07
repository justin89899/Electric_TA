import os
import pandas as pd
import fitz  # PyMuPDF for handling PDFs
from openai import OpenAI
from dotenv import load_dotenv
import dropbox
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from ast import literal_eval

# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def find_relevant_chunk(chunks_embedding, answer_embedding):
    highest_similarity = -1
    most_relevant_chunk_index = -1

    for index, chunk_embedding in enumerate(chunks_embedding):
        
        similarity = cosine_similarity(chunk_embedding, answer_embedding)
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_relevant_chunk_index = index

    return most_relevant_chunk_index


def process_answers(text_chunk_csv, answers):
    # Read the chunks from the CSV file
    df = pd.read_csv(text_chunk_csv)
    df['embedding'] = df['embedding'].apply(lambda x: literal_eval(x))
    chunks_embedding = df['embedding'].tolist()

    for answer in answers:
        answer_embedding = get_embedding(answer)
        relevant_chunk_index = find_relevant_chunk(chunks_embedding, answer_embedding)

        # Get the relevant chunk and its details from the DataFrame
        relevant_chunk = df.iloc[relevant_chunk_index]
        chunk_text = relevant_chunk['Text']
        chunk_index = relevant_chunk['Index']
        match = re.search(r'Lecture(\d+)_Chunk', chunk_index)
        lecture_number = int(match.group(1))
        print(f"Answer: {answer}\nRelevant chunk: {chunk_index}\nChunk text: {chunk_text}\n")
        return chunk_index, chunk_text, lecture_number


def find_matching_timestamps(transcript_map, text_chunk):
    matching_timestamp = -1
    answer_embedding = get_embedding(text_chunk)
    highest_similarity = -1
    most_relevant_timestamp = ""
    for timestamp, transcript_text_embedding in transcript_map.items():
        transcript_text, transcript_embedding = transcript_text_embedding
        similarity = cosine_similarity(answer_embedding, transcript_embedding)
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_relevant_timestamp = timestamp

        matching_timestamp = most_relevant_timestamp

    return matching_timestamp


def find_time_stamps(lecture_number, text_chunk):

    # Read the lecture json file
    file_path = f'transcripts/lecture-{lecture_number}.json'
    # Opening and reading the JSON file
    with open(file_path, 'r') as file:
        lecture_data = json.load(file)

    # get the timestamp and text pair
    transcript_map = lecture_data['transcript']

    # STEP6
    # Match the time stamps with our chunk
    matching_timestamp = find_matching_timestamps(transcript_map, text_chunk)
    print('matching timestamp',matching_timestamp)
    if not matching_timestamp or type(matching_timestamp) != str:
        return None, None
    m = matching_timestamp.split(":")
    time_stamp = int(m[0]) * 60 + int(m[1])
    print(m, time_stamp)

    youtube_base_link = lecture_data['youtube_base_link']
    final_youtube_timestamps_link = youtube_base_link + f"?start={time_stamp}"
    print(final_youtube_timestamps_link)
    return final_youtube_timestamps_link, f"{m[0]}m{m[1]}s"

# import os
# import pandas as pd
# import fitz  # PyMuPDF for handling PDFs
# from openai import OpenAI
# from dotenv import load_dotenv
# import dropbox
# import numpy as np
# import requests
# from bs4 import BeautifulSoup
# import re
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import json

# # Load environment variables from .env file
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# def get_embedding(text, model="text-embedding-3-small"):
#     text = text.replace("\n", " ")
#     return client.embeddings.create(input=[text], model=model).data[0].embedding


# def cosine_similarity(vec1, vec2):
#     return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


# def find_relevant_chunk(chunks, answer_embedding):
#     highest_similarity = -1
#     most_relevant_chunk_index = -1

#     for index, chunk in enumerate(chunks):
#         chunk_embedding = get_embedding(chunk)
#         similarity = cosine_similarity(chunk_embedding, answer_embedding)
#         if similarity > highest_similarity:
#             highest_similarity = similarity
#             most_relevant_chunk_index = index

#     return most_relevant_chunk_index


# def process_answers(text_chunk_csv, answers):
#     # Read the chunks from the CSV file
#     df = pd.read_csv(text_chunk_csv)
#     chunks = df['Text'].tolist()

#     for answer in answers:
#         answer_embedding = get_embedding(answer)
#         relevant_chunk_index = find_relevant_chunk(chunks, answer_embedding)

#         # Get the relevant chunk and its details from the DataFrame
#         relevant_chunk = df.iloc[relevant_chunk_index]
#         chunk_text = relevant_chunk['Text']
#         chunk_index = relevant_chunk['Index']
#         match = re.search(r'Lecture(\d+)_Chunk', chunk_index)
#         lecture_number = int(match.group(1))
#         print(f"Answer: {answer}\nRelevant chunk: {chunk_index}\nChunk text: {chunk_text}\n")
#         return chunk_index, chunk_text, lecture_number


# def find_matching_timestamps(transcript_lines, text_chunk):
#     matching_timestamp = -1
#     answer_embedding = get_embedding(text_chunk)
#     highest_similarity = -1
#     most_relevant_timestamp = ""
#     for line in transcript_lines:
#         transcript_text = line.find('span', class_='transcript-text').get_text().replace('\n', ' ')
#         transcript_embedding = get_embedding(transcript_text)
#         similarity = cosine_similarity(answer_embedding, transcript_embedding)
#         if similarity > highest_similarity:
#             highest_similarity = similarity
#             most_relevant_timestamp = line.find('span', class_='transcript-timestamp').get_text()

#         matching_timestamp = most_relevant_timestamp

#     return matching_timestamp


# def find_time_stamps(lecture_number, text_chunk):
#     course_home_url = 'https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/'
#     course_home_base_url = 'https://ocw.mit.edu'

#     # STEP1:
#     # Fetch the course home page
#     response = requests.get(course_home_url)
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # STEP2:
#     # Define the regular expression pattern for lecture video links
#     pattern = re.compile("lecture-videos")

#     # Find all links that contain the pattern "lecture-videos" in their 'href'
#     lecture_videos = soup.find_all('a', href=pattern)[0]['href']

#     # Find the lecture videos links
#     lecture_video_link = course_home_base_url + lecture_videos
#     print(lecture_video_link)

#     # STEP3:
#     # Go to lecture videos page to find specific lecture
#     response = requests.get(lecture_video_link)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     pattern_specific = re.compile(f"lecture-{lecture_number}")

#     specific_lecture_link = course_home_base_url + soup.find_all('a', class_="video-link", href=pattern_specific)[0]['href']
#     print(specific_lecture_link)

#     # STEP4:
#     # Find the transcript section on the lecture page
#     # Set up webdriver
#     driver = webdriver.Chrome()

#     # Replace this with the actual URL you need to load
#     driver.get(specific_lecture_link)

#     # Wait for the transcript button to be clickable, and then click it
#     transcript_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.CSS_SELECTOR, "button.tab-toggle-button"))
#     )
#     transcript_button.click()

#     # Wait for the transcript-body
#     element = WebDriverWait(driver, 20).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "transcript-body"))
#     )

#     # Now that the transcript content has been loaded, we can parse it with BeautifulSoup
#     html_content = driver.page_source
#     soup = BeautifulSoup(html_content, 'html.parser')

#     # STEP5
#     # Find the transcript text and timestamps
#     transcript_body = soup.find('div', class_='transcript-body')
#     if transcript_body:
#         transcript_lines = transcript_body.find_all('div', class_='transcript-line')
#         for line in transcript_lines:
#             # Extract timestamp and text here
#             timestamps = line.find('span', class_='transcript-timestamp').get_text()
#             text = line.find('span', class_='transcript-text').get_text()
#             print(f"{timestamps} : {text}")
#     else:
#         print("transcript_body:", transcript_body)
#         return None, None

#     # STEP6
#     # Match the time stamps with our chunk
#     matching_timestamp = find_matching_timestamps(transcript_lines, text_chunk)
#     print("matching_timestamp:", matching_timestamp)
#     if not matching_timestamp or type(matching_timestamp) != str:
#         return None, None
#     m = matching_timestamp.split(":")
#     time_stamp = int(m[0]) * 60 + int(m[1])
#     print(m, time_stamp)

#     # STEP7
#     # Find the YouTube link
#     # Find the element with the data-setup attribute
#     # Find the container div
#     container_div = soup.find('div', class_='video-container embedded-video-container youtube-container')

#     # Find the first child div with the 'aria-label' attribute within the container
#     child_div_with_aria_label = container_div.find('div', attrs={'aria-label': True})
#     youtube_base_link = json.loads(child_div_with_aria_label['data-setup'])['sources'][0]['src']
#     final_youtube_timestamps_link = youtube_base_link + f"?start={time_stamp}"
#     print(final_youtube_timestamps_link)
#     return final_youtube_timestamps_link, f"{m[0]}m{m[1]}s"
