import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def download_slides():
    folder = "Lectures/slides"

    if not os.path.exists(folder):
        os.makedirs(folder)

    course_url = "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/"
    response = requests.get(course_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    lecture_slide_site = soup.find('a', {'data-uuid': "f39a25a3-5f6b-0d3e-6388-e9b2e8b7438e"})["href"]

    # lecture slides and code webpage
    url = "https://ocw.mit.edu"
    lecture_slide_site = url + lecture_slide_site
    response = requests.get(lecture_slide_site)
    soup = BeautifulSoup(response.text, 'html.parser')

    # for each lecture, find the slides
    links = soup.find_all('tr')

    for i in links[1:]:
        list = i.find_all('td')
        lecture_number = list[0].text.strip()
        lecture_slides_link = url + list[2].find('a')['href']
        response = requests.get(lecture_slides_link)
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_link = url + soup.find('a', {'class': 'download-link'})['href']

        # download pdf
        pdf_response = requests.get(pdf_link)
        file_path = os.path.join(folder, f"Lecture{lecture_number}.pdf")
        with open(file_path, 'wb') as f:
            f.write(pdf_response.content)

def download_transcripts():
    folder = "documents"

    if not os.path.exists(folder):
        os.makedirs(folder)
    
    driver_path = "chromedriver-win64/chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_experimental_option('detach', True)
    service = webdriver.ChromeService(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    lecture_videos_site = "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/video_galleries/lecture-videos/"
    response = requests.get(lecture_videos_site)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', {'class': 'video-link'})

    url = "https://ocw.mit.edu"

    for i in links:
        lesson_url = url + i['href']

        driver.get(lesson_url)
        time.sleep(0.1)
        lecture_info = driver.find_element(By.XPATH, '//h2[@class="pb-1 mb-1"]').text
        lecture_number = lecture_info.split(':')[0].split(' ')[1]
        download_icon = driver.find_element(By.XPATH, '//button[@class="video-download-icons"]')
        download_icon.click()
        download_link = driver.find_element(By.XPATH, '//li/a[@aria-label="Download transcript"]')
        transcript = download_link.get_attribute('href')

        pdf_response = requests.get(transcript)
        file_path = os.path.join(folder, f"lecture {lecture_number} transcript.pdf")
        with open(file_path, 'wb') as f:
            f.write(pdf_response.content)
    
    driver.quit()


download_slides()
download_transcripts()


