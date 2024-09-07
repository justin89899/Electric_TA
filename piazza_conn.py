import sys
from piazza_api import Piazza
import pandas as pd
from bs4 import BeautifulSoup
import json
import time
import os


def create_piazza_object():
    p = Piazza()
    return p


def login_to_piazza(p, Email, Password):
    # Log in the user with the specified email and password
    try:
        p.user_login(Email, Password)
        return True
    except:
        print("Login Failed!")
        return None


def get_user_profile(p):
    user_profile = p.get_user_profile()
    return user_profile


def get_course_network(p, network_id):
    course = p.network(network_id)
    return course


# Function to extract posts and save to a list
def extract_posts(course):
    raw_datas = course.iter_all_posts(sleep=1)
    all_data_posts = []

    for raw_data in raw_datas:
        data_post = {}
        data_post["Question Number"] = raw_data['nr']
        data_post["Question ID"] = raw_data['id']
        data_post["Question folders"] = raw_data['folders']
        data_post["Tags"] = raw_data['tags']
        list_posts = raw_data["history"]
        for post in list_posts:
            subject = post["subject"]
            text_subject = BeautifulSoup(subject, 'html.parser').get_text()

            question_content = post["content"]
            text_question = BeautifulSoup(question_content, 'html.parser').get_text()
            data_post["Subject"] = text_subject
            data_post["Question Content"] = text_question if text_question else text_subject

        list_response = raw_data["children"]
        all_data_posts.append(data_post)
        answers_lists = []
        for response in list_response:
            try:
                response_contents = response["history"]
                for content in response_contents:
                    response_content = content["content"]
                    text_response = BeautifulSoup(response_content, 'html.parser').get_text()

                    if len(text_response) > 1:
                        answers_lists.append(text_response)
            except KeyError:
                print("No response key found")
        data_post['Response Content'] = answers_lists

    return all_data_posts


def save_to_csv(data_posts, file_name):
    # Define the directory path
    folder_name = "piazza_data"

    # Check if the folder exists, and create it if it doesn't
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Create the full file path
    file_path = os.path.join(folder_name, file_name)

    # Convert data to DataFrame and save it to the specified file
    df = pd.json_normalize(data_posts)
    df.to_csv(file_path, index=False)
    print(f"File saved to {file_path}")


# Function to filter out unanswered posts
def get_unanswered_questions(all_data_posts):
    unanswered_questions = []
    answered_questions_and_instructor_notes = []
    for post in all_data_posts:
        if "instructor-note" in post['Tags']:
            answered_questions_and_instructor_notes.append(post)
        else:
            if not post['Response Content']:
                unanswered_questions.append(post)
            else:
                answered_questions_and_instructor_notes.append(post)
    return unanswered_questions, answered_questions_and_instructor_notes


def run():
    p = create_piazza_object()

    # Ask user to input Email and Password
    Email = input("Please Enter Your Email: ")
    Password = input("Please Enter Your Password: ")
    login_to_piazza(p, Email, Password)

    # Example Network ID
    network_id = "ltov6kuqfcn74l"
    course = get_course_network(p, network_id)

    # Retrieve all the current posts: Both answered and unanswered
    all_data_posts = extract_posts(course)

    # Filter out the answered posts and store the rest unanswered questions in a list
    unanswered_questions, answered_questions_and_instructor_notes = get_unanswered_questions(all_data_posts)

    # save to database/csv
    save_to_csv(all_data_posts, "piazza_all_content.csv")
    save_to_csv(unanswered_questions, "piazza_unanswered_questions.csv")
    save_to_csv(answered_questions_and_instructor_notes, "piazza_answered_or_instru_notes.csv")


# if __name__ == "__main__":
#     run()
