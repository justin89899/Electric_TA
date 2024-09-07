import sys
from piazza_api import Piazza
from piazza_api.rpc import PiazzaRPC
import pandas as pd
from bs4 import BeautifulSoup
import json
import time
import piazza_conn


# Make RPC Connection
def piazza_rpc_conn(network_id, email, password):
    p_rpc = PiazzaRPC(network_id)
    p_rpc.user_login(email, password)
    return p_rpc


# respond to piazza
def respond_to_all_piazza(p_rpc, unanswered_questions):
    status = p_rpc.get_user_profile()
    for question in unanswered_questions:
        cid = question['Question ID']
        content = "I am an AI and I will respond to you shortly!"
        question['Response Content'].append(content)
        try:
            response_from_instructor(p_rpc, cid, content)
        except:
            response_from_student(p_rpc, cid, content)
    return unanswered_questions


def respond_to_piazza(p_rpc, unanswered_questions, cid, content):
    try:
        response_from_instructor(p_rpc, cid, content)
    except:
        response_from_student(p_rpc, cid, content)
    return unanswered_questions


# Function to call rpc instructor response
def response_from_instructor(p_rpc, cid, content):
    params = {
        "cid": cid,  # The ID of the post you're answering
        "type": "i_answer",
        "revision": 1,
        "content": content,  # The content of your answer
    }

    p_rpc.content_instructor_answer(params)


# Function to call rpc student response
def response_from_student(p_rpc, cid, content):
    p_rpc.content_student_answer(cid, content, 1, False)


# main running function
def run_answer(cid, content):
    # connect to Piazza API
    p = piazza_conn.create_piazza_object()
    email = input("Please Enter Your Email: ")
    password = input("Please Enter Your Password: ")
    piazza_conn.login_to_piazza(p, email, password)

    # Connect to a specified course: CS101 Mock Course
    network_id = "ltov6kuqfcn74l"
    course = piazza_conn.get_course_network(p, network_id)

    # Retrieve all the current posts: Both answered and unanswered
    all_data_posts = piazza_conn.extract_posts(course)

    # Filter out the answered posts and store the rest unanswered questions in a list
    unanswered_questions, answered_questions_and_instructor_notes = piazza_conn.get_unanswered_questions(all_data_posts)

    # connect to piazza_rpc to access more functions
    p_rpc = piazza_rpc_conn(network_id, email, password)

    # post as a Student / Instructor and respond to the unanswered questions
    responded_posts = respond_to_piazza(p_rpc, unanswered_questions, cid, content)
    piazza_conn.save_to_csv(responded_posts, "piazza_unanswered_questions_response.csv")


# if __name__ == "__main__":
#     cid = None
#     content = None
#     run_answer(cid, content)

