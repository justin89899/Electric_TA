import piazza_conn
import piazza_answer
import chatbot_text_only
import slides_snapshot
import os
import dropbox
import re
import video_timestamps
from dropbox.exceptions import ApiError
import time

def process_question_from_web(question, email, password):

    # start time
    start_time = time.time()

    # Step 1: Connect to piazza and retrieve all data posts
    p = piazza_conn.create_piazza_object()
    piazza_conn.login_to_piazza(p, email, password)

    # Example Network ID
    network_id = "ltov6kuqfcn74l"
    course = piazza_conn.get_course_network(p, network_id)

    check1 = time.time()

    # 2. Step 2: Embedding and pass to GPT
    # transcript text
    #text_chunks = chatbot_text_only.load_text_chunks('text_chunks.csv')

    # piazza text
    piazza_text_chunks = chatbot_text_only.make_piazza_text_chunks("piazza_data/piazza_answered_or_instru_notes.csv")

    # get the transcript texts vectors and create answered text on piazza to vectors
    vectorstore = chatbot_text_only.get_text_chunks_vectorstore()
    piazza_vectorstore = chatbot_text_only.get_vectorstore(piazza_text_chunks)

    # combine the vectors
    vectorstore.merge_from(piazza_vectorstore)
    conversation_chain = chatbot_text_only.get_conversation_chain(vectorstore)

    # 3. Answer all unanswered questions with snapshots
    # slides pdf folder
    precomputed_embeddings_path = "slides_embeddings.json"
    # slides_pdf_folder = "Lectures/slides"
    # pdf_paths = [os.path.join(slides_pdf_folder, f) for f in os.listdir(slides_pdf_folder) if f.endswith('.pdf')]
    check2 = time.time()
    print(question)
    # 1. Answer
    bot_response = \
        f"{chatbot_text_only.handle_userinput(question, conversation_chain)}"
    print(bot_response)
    if "sorry" in bot_response.lower():
        return {
            'answer': bot_response,
            'snapshot': None,
            'url': None
        }
    
    # 2. Snapshot
    # Find the most relevant slide for the current question's answer
    most_relevant_snapshot_path = slides_snapshot.process_answers(precomputed_embeddings_path, [bot_response])
    snapshot_filename = os.path.basename(most_relevant_snapshot_path)
    # Construct a URL for the image
    snapshot_url = f"http://127.0.0.1:5000/snapshots/{snapshot_filename}"

    # 3. Video Timestamps & link
    # Find the most relevant index chunk for the current question's answer in the lecture video
    lecture_index,  lecture_text, lecture_number = video_timestamps.process_answers("text_chunks_with_embedding.csv", [bot_response])
    
    youtube_link, timestamp = video_timestamps.find_time_stamps(lecture_number, lecture_text)

    # # 4. Combine the bot's response with the snapshot information and video link
    final_response = {
        'answer': bot_response,
        'snapshot': snapshot_url,
        'url': youtube_link
    }

    end_time = time.time()
    print(f'checkpoint 1: {check1 - start_time}')
    print(f'checkpoint 2: {check2 - check1}')
    print(f'checkpoint 3: {end_time - check2}')
    print(f'Run time: {end_time - start_time}')

    return final_response


def run_all():
    # Step 1: Connect to piazza and retrieve all data posts
    p = piazza_conn.create_piazza_object()

    # Ask user to input Email and Password
    Email = input("Please Enter Your Email: ")
    Password = input("Please Enter Your Password: ")
    piazza_conn.login_to_piazza(p, Email, Password)

    # Example Network ID
    network_id = "ltov6kuqfcn74l"
    course = piazza_conn.get_course_network(p, network_id)

    # start time
    start_time = time.time()

    # Retrieve all the current posts: Both answered and unanswered
    all_data_posts = piazza_conn.extract_posts(course)
    
    # checkpoint extract_posts
    check_extract_posts = time.time()
    print('check_extract_posts', check_extract_posts - start_time)

    # Filter out the answered posts and store the rest unanswered questions in a list
    unanswered_questions, answered_questions_and_instructor_notes = piazza_conn.get_unanswered_questions(all_data_posts)
    # checkpoint extract_posts
    check_get_unanswered_questions = time.time()
    print('check_get_unanswered_questions', check_get_unanswered_questions - check_extract_posts)

    # save the results for safety reason
    piazza_conn.save_to_csv(answered_questions_and_instructor_notes, "piazza_answered_or_instru_notes.csv")
    piazza_conn.save_to_csv(all_data_posts, "piazza_all_content.csv")
    piazza_conn.save_to_csv(unanswered_questions, "piazza_unanswered_questions.csv")

    if not unanswered_questions:
        print("All questions have been answered!")
        end_time = time.time()
        print(f'Run time: {end_time - start_time}')
        return

    # checkpoint 1
    check1 = time.time()

    # 2. Step 2: Embedding and pass to GPT
    # transcript text
    #text_chunks = chatbot_text_only.load_text_chunks('text_chunks.csv')

    # piazza text
    piazza_text_chunks = chatbot_text_only.make_piazza_text_chunks("piazza_data/piazza_answered_or_instru_notes.csv")

    # get the transcript texts vectors and create answered text on piazza to vectors
    vectorstore = chatbot_text_only.get_text_chunks_vectorstore()
    piazza_vectorstore = chatbot_text_only.get_vectorstore(piazza_text_chunks)

    # coombine the vectors
    vectorstore.merge_from(piazza_vectorstore)
    conversation_chain = chatbot_text_only.get_conversation_chain(vectorstore)

    # checkpoint 2
    check2 = time.time()

    # 3. Answer all unanswered questions with snapshots
    # slides pdf folder
    slides_pdf_folder = "Lectures/slides"
    pdf_paths = [os.path.join(slides_pdf_folder, f) for f in os.listdir(slides_pdf_folder) if f.endswith('.pdf')]
    # connect to piazza_rpc to access more functions
    p_rpc = piazza_answer.piazza_rpc_conn(network_id, Email, Password)

    # Loop through the unanswered questions and provides response
    for question in unanswered_questions:
        
        # 1. Answer
        bot_response = \
            f"{chatbot_text_only.handle_userinput(question['Question Content'], conversation_chain)}, answered by AI"
        cid = question["Question ID"]
        
        # 2. Snapshot
        # Find the most relevant slide for the current question's answer
        # most_relevant_snapshot_path = slides_snapshot.process_answers(pdf_paths, [bot_response])

        # access_token = ''
        # dbx = dropbox.Dropbox(access_token)
        # dropbox_uploaded = slides_snapshot.upload_to_dropbox(most_relevant_snapshot_path, access_token)

        # if dropbox_uploaded:
        #     file_path_on_dropbox = dropbox_uploaded.path_display
        #     try:
        #         # Attempt to create a shareable link
        #         shareable_link_metadata = dbx.sharing_create_shared_link_with_settings(file_path_on_dropbox)
        #         shareable_link = shareable_link_metadata.url
        #     except ApiError as e:
        #         if isinstance(e.error, dropbox.sharing.CreateSharedLinkWithSettingsError) and \
        #                 e.error.is_shared_link_already_exists():
        #             # If the link already exists, fetch the existing shareable link
        #             existing_links = dbx.sharing_list_shared_links(path=file_path_on_dropbox).links
        #             if existing_links:
        #                 shareable_link = existing_links[0].url
        #             else:
        #                 print("Failed to retrieve existing shareable link.")
        #                 shareable_link = None
        #     match = re.search(r"/([^/]+)_slide_\d+\.png", shareable_link)
        #     lecture = match.group(1) if match else None
        #     print(lecture)
        #     print(f"Shareable link: {shareable_link}")
        
        
        # 3. Video Timestamps & link
        # Find the most relevant index chunk for the current question's answer in the lecture video
        lecture_index,  lecture_text, lecture_number = video_timestamps.process_answers("text_chunks_with_embedding.csv", [bot_response])
        
        youtube_link, timestamp = video_timestamps.find_time_stamps(lecture_number, lecture_text)
        
        # 4. Combine the bot's response with the snapshot information
        final_response = (f'{bot_response}\n\n '
                          #f'You can see detail in slide {lecture}: <a href="{shareable_link}">Slide Image</a>\n'
                          f'You can also view detail explanation in Lecture Video {lecture_number} - {timestamp}: '
                          f'<a href="{youtube_link}">Lecture Video</a> ')

        responded_posts = piazza_answer.respond_to_piazza(p_rpc, unanswered_questions, cid, final_response)
        piazza_conn.save_to_csv(responded_posts, "piazza_unanswered_questions_response.csv")
        
    end_time = time.time()
    print(f'checkpoint 1: {check1 - start_time}')
    print(f'checkpoint 2: {check2 - check1}')
    print(f'checkpoint 3: {end_time - check2}')
    print(f'Run time: {end_time - start_time}')

if __name__ == "__main__":
    run_all()


# def run_all():
#     # Step 1: Connect to piazza and retrieve all data posts
#     p = piazza_conn.create_piazza_object()

#     # Ask user to input Email and Password
#     Email = input("Please Enter Your Email: ")
#     Password = input("Please Enter Your Password: ")
#     piazza_conn.login_to_piazza(p, Email, Password)

#     # Example Network ID
#     network_id = "ltov6kuqfcn74l"
#     course = piazza_conn.get_course_network(p, network_id)

#     # Retrieve all the current posts: Both answered and unanswered
#     all_data_posts = piazza_conn.extract_posts(course)

#     # Filter out the answered posts and store the rest unanswered questions in a list
#     unanswered_questions, answered_questions_and_instructor_notes = piazza_conn.get_unanswered_questions(all_data_posts)

#     # save the results for safety reason
#     piazza_conn.save_to_csv(answered_questions_and_instructor_notes, "piazza_answered_or_instru_notes.csv")
#     piazza_conn.save_to_csv(all_data_posts, "piazza_all_content.csv")
#     piazza_conn.save_to_csv(unanswered_questions, "piazza_unanswered_questions.csv")

#     if not unanswered_questions:
#         print("All questions have been answered!")
#         return

#     # 2. Step 2: Embedding and pass to GPT
#     # transcript text
#     text_chunks = chatbot_text_only.load_text_chunks('text_chunks.csv')

#     # piazza text
#     piazza_text_chunks = chatbot_text_only.make_piazza_text_chunks("piazza_data/piazza_answered_or_instru_notes.csv")

#     # Combine the transcript texts and answered text on piazza to create vectors
#     vectorstore = chatbot_text_only.get_vectorstore(text_chunks + piazza_text_chunks)
#     conversation_chain = chatbot_text_only.get_conversation_chain(vectorstore)

#     # 3. Answer all unanswered questions with snapshots
#     # slides pdf folder
#     slides_pdf_folder = "Lectures/slides"
#     pdf_paths = [os.path.join(slides_pdf_folder, f) for f in os.listdir(slides_pdf_folder) if f.endswith('.pdf')]
#     # connect to piazza_rpc to access more functions
#     p_rpc = piazza_answer.piazza_rpc_conn(network_id, Email, Password)

#     # Loop through the unanswered questions and provides response
#     for question in unanswered_questions:
#         # 1. Answer
#         bot_response = \
#             f"{chatbot_text_only.handle_userinput(question['Question Content'], conversation_chain)}, answered by AI"
#         cid = question["Question ID"]

#         # 2. Snapshot
#         # Find the most relevant slide for the current question's answer
#         most_relevant_snapshot_path = slides_snapshot.process_answers(pdf_paths, [bot_response])

#         access_token = ''
#         dbx = dropbox.Dropbox(access_token)
#         dropbox_uploaded = slides_snapshot.upload_to_dropbox(most_relevant_snapshot_path, access_token)

#         if dropbox_uploaded:
#             file_path_on_dropbox = dropbox_uploaded.path_display
#             try:
#                 # Attempt to create a shareable link
#                 shareable_link_metadata = dbx.sharing_create_shared_link_with_settings(file_path_on_dropbox)
#                 shareable_link = shareable_link_metadata.url
#             except ApiError as e:
#                 if isinstance(e.error, dropbox.sharing.CreateSharedLinkWithSettingsError) and \
#                         e.error.is_shared_link_already_exists():
#                     # If the link already exists, fetch the existing shareable link
#                     existing_links = dbx.sharing_list_shared_links(path=file_path_on_dropbox).links
#                     if existing_links:
#                         shareable_link = existing_links[0].url
#                     else:
#                         print("Failed to retrieve existing shareable link.")
#                         shareable_link = None
#             match = re.search(r"/([^/]+)_slide_\d+\.png", shareable_link)
#             lecture = match.group(1) if match else None
#             print(lecture)
#             print(f"Shareable link: {shareable_link}")

#         # 3. Video Timestamps & link
#         # Find the most relevant index chunk for the current question's answer in the lecture video
#         lecture_index,  lecture_text, lecture_number = video_timestamps.process_answers("text_chunks.csv", [bot_response])
#         youtube_link, timestamp = video_timestamps.find_time_stamps(lecture_number, lecture_text)

#         # 4. Combine the bot's response with the snapshot information
#         final_response = (f'{bot_response}\n\n '
#                           f'You can see detail in slide {lecture}: <a href="{shareable_link}">Slide Image</a>\n'
#                           f'You can also view detail explanation in Lecture Video {lecture_number} - {timestamp}: '
#                           f'<a href="{youtube_link}">Lecture Video</a> ')

#         responded_posts = piazza_answer.respond_to_piazza(p_rpc, unanswered_questions, cid, final_response)
#         piazza_conn.save_to_csv(responded_posts, "piazza_unanswered_questions_response.csv")


# if __name__ == "__main__":
#     run_all()
