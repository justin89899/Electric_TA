from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import os
import pandas as pd
from transcript_to_chunks import get_text_chunks
from dotenv import load_dotenv
import warnings
from langchain_core._api.deprecation import LangChainDeprecationWarning
import piazza_answer

# Suppress LangChainDeprecationWarnings
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

# Load environment variables from .env file
load_dotenv()


# load text chunks from text_chunks.csv
def load_text_chunks(file_name):
    text_chunks = pd.read_csv(file_name)['Text']
    return text_chunks.to_list()


# make text chunks from piazza_answered_or_instru_notes.csv
def make_piazza_text_chunks(csv_path):
    piazza_text = ""
    piazza_answered_or_instru_notes = pd.read_csv(csv_path)
    for i in range(len(piazza_answered_or_instru_notes)):
        post = piazza_answered_or_instru_notes.iloc[i, :]
        if "instructor-note" in post.Tags:
            piazza_text += post["Question Content"]
        else:
            piazza_text += post["Question Content"]
            piazza_text += post["Response Content"]
    
    piazza_text_chunks = get_text_chunks(piazza_text)
    return piazza_text_chunks


# embeddings
def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


# get pre calculated vectorstore
def get_text_chunks_vectorstore():
    embeddings = OpenAIEmbeddings()
    text_chunks_vectorstore = FAISS.load_local("text_chunks_faiss_index", embeddings, allow_dangerous_deserialization=True)
    return text_chunks_vectorstore


# conversation chain
def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}),
        memory=memory,
    )
    return conversation_chain


# chat_history is: user, bot, user, bot, ...
def handle_userinput(user_question, conversation_chain):
    response = conversation_chain({'question': user_question})
    chat_history = response['chat_history']

    return chat_history[-1].content




# from dotenv import load_dotenv
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain_openai import ChatOpenAI
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import ConversationalRetrievalChain
# import os
# import pandas as pd
# from transcript_to_chunks import get_text_chunks
# from dotenv import load_dotenv
# import warnings
# from langchain_core._api.deprecation import LangChainDeprecationWarning
# import piazza_answer

# # Suppress LangChainDeprecationWarnings
# warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

# # Load environment variables from .env file
# load_dotenv()


# # load text chunks from text_chunks.csv
# def load_text_chunks(file_name):
#     text_chunks = pd.read_csv(file_name)['Text']
#     return text_chunks.to_list()


# # make text chunks from piazza_answered_or_instru_notes.csv
# def make_piazza_text_chunks(csv_path):
#     piazza_text = ""
#     piazza_answered_or_instru_notes = pd.read_csv(csv_path)
#     for i in range(len(piazza_answered_or_instru_notes)):
#         post = piazza_answered_or_instru_notes.iloc[i, :]
#         if "instructor-note" in post.Tags:
#             piazza_text += post["Question Content"]
#         else:
#             piazza_text += post["Question Content"]
#             piazza_text += post["Response Content"]
    
#     piazza_text_chunks = get_text_chunks(piazza_text)
#     return piazza_text_chunks


# # embeddings
# def get_vectorstore(text_chunks):
#     embeddings = OpenAIEmbeddings()
#     vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
#     return vectorstore


# # conversation chain
# def get_conversation_chain(vectorstore):
#     llm = ChatOpenAI()
#     memory = ConversationBufferMemory(
#         memory_key='chat_history', return_messages=True)
#     conversation_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=vectorstore.as_retriever(
#             search_type="similarity", search_kwargs={"k": 4}),
#         memory=memory,
#     )
#     return conversation_chain


# # chat_history is: user, bot, user, bot, ...
# def handle_userinput(user_question, conversation_chain):
#     response = conversation_chain({'question': user_question})
#     chat_history = response['chat_history']

#     return chat_history[-1].content


#
# def main():
#     #questions to be answered
#     unanswered = pd.read_csv("piazza_data/piazza_unanswered_questions.csv").to_dict(orient='records')
#     if len(unanswered) == 0:
#         return
#
#     # transcript text
#     text_chunks = load_text_chunks('text_chunks.csv')
#
#     # piazza text
#     piazza_text_chunks = make_piazza_text_chunks("piazza_data/piazza_answered_or_instru_notes.csv")
#
#     vectorstore = get_vectorstore(text_chunks + piazza_text_chunks)
#     conversation_chain = get_conversation_chain(vectorstore)
#
#     # currently answer in terminal
#     for question in unanswered:
#         bot_response = f"{handle_userinput(question['Question Content'], conversation_chain)}, answered by AI"
#         cid = question["Question ID"]
#         print(question["Question Content"])
#         print(bot_response)
#         piazza_answer.run_answer(cid, bot_response)
#
#
# main()
