import os
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def scrape_all_transcripts():
    course_home_url = 'https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/'
    course_home_base_url = 'https://ocw.mit.edu'

    # STEP1:
    # Fetch the course home page
    response = requests.get(course_home_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # STEP2:
    # Define the regular expression pattern for lecture video links
    pattern = re.compile("lecture-videos")

    # Find all links that contain the pattern "lecture-videos" in their 'href'
    lecture_videos = soup.find_all('a', href=pattern)[0]['href']

    # Find the lecture videos links
    lecture_video_link = course_home_base_url + lecture_videos
    print(lecture_video_link)

    # STEP3:
    # Go to lecture videos page to find specific lecture
    response = requests.get(lecture_video_link)
    soup = BeautifulSoup(response.content, 'html.parser')

    pattern_specific = re.compile(f"lecture-")

    # Iterate through all the lecture numbers
    all_lecture_find = soup.find_all('a', class_="video-link", href=pattern_specific)
    for found_lec_link in all_lecture_find:
        timestamp_text_map = {}

        specific_lecture_link = course_home_base_url + found_lec_link['href']
        print(specific_lecture_link)

        # STEP4:
        # Find the transcript section on the lecture page
        # Set up webdriver
        driver = webdriver.Chrome()

        # Replace this with the actual URL you need to load
        driver.get(specific_lecture_link)

        # Wait for the transcript button to be clickable, and then click it
        transcript_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.tab-toggle-button"))
        )
        transcript_button.click()

        # Wait for the transcript-body
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "transcript-body"))
        )

        # Now that the transcript content has been loaded, we can parse it with BeautifulSoup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # STEP5
        # Find the transcript text and timestamps
        transcript_body = soup.find('div', class_='transcript-body')
        if transcript_body:
            transcript_lines = transcript_body.find_all('div', class_='transcript-line')
            counter = 0
            text_chunk = ''
            for line in transcript_lines:

                if counter == 0:
                    timestamps = line.find('span', class_='transcript-timestamp').get_text()
                    text = line.find('span', class_='transcript-text').get_text()
                    text_chunk += text
                else:
                    text = line.find('span', class_='transcript-text').get_text()
                    text_chunk += text
                counter+=1
                # accumulate 10 timestamps, then embedd and reset counter
                if counter == 10:
                    embedding = get_embedding(text_chunk)
                    timestamp_text_map[timestamps] = (text_chunk, embedding)
                    text_chunk = ''
                    counter = 0
            # last chunk
            if text_chunk:
                embedding = get_embedding(text_chunk)
                timestamp_text_map[timestamps] = (text_chunk, embedding)
                
        else:
            print("coundn't find transcrip for lecture", found_lec_link['href'])
            continue


        # STEP6
        # Find the YouTube link
        # Find the element with the data-setup attribute
        # Find the container div
        container_div = soup.find('div', class_='video-container embedded-video-container youtube-container')

        # Find the first child div with the 'aria-label' attribute within the container
        child_div_with_aria_label = container_div.find('div', attrs={'aria-label': True})
        youtube_base_link = json.loads(child_div_with_aria_label['data-setup'])['sources'][0]['src']

        output_to_save = {}
        output_to_save['youtube_base_link'] = youtube_base_link
        output_to_save['transcript'] = timestamp_text_map

        # Step 7 save it to json file
        # Specify the filename
        filepth = f"transcripts/{re.search('/lecture-[0-9]+-', found_lec_link['href']).group()[1:-1]}.json"

        
        # Writing JSON data
        with open(filepth, 'w') as file:
            json.dump(output_to_save, file, indent=4)

        print(f'Saved transcripts to {filepth}.')

    print('Saved all the lecture transcipts that are available.')
scrape_all_transcripts()