from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import pyttsx3
import speech_recognition as sr
import time
from threading import Thread
import os, openai
from langchain.memory import ConversationBufferWindowMemory
import pandas as pd
from langchain.llms import OpenAI
from langchain.agents.agent_types import AgentType
from langchain.agents import create_csv_agent
import json
import requests
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory

app = Flask(__name__, static_url_path='/static')

os.environ["OPENAI_API_KEY"] = "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"

def speak_text(text, rate=150):
    engine = pyttsx3.init(driverName='sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

r = sr.Recognizer()
chat_history = []

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

response_speaking = False

def background_speak(response):
    global response_speaking  # Declare response_speaking as a global variable
    if not response_speaking:
        response_speaking = True  # Set response_speaking to True when speaking starts
        speak_text(response)
        response_speaking = False



@app.route('/', methods=['POST','GET'])
def index():
    if request.method == "POST":        
        uploaded_file = request.files['file']
        print(uploaded_file)
        if uploaded_file and uploaded_file.filename != '':
            if uploaded_file.filename.endswith('.pdf'):
                uploaded_file.save('uploaded_pdf.pdf')

            elif uploaded_file.filename.endswith(('.xls', '.xlsx', '.csv')):
                if uploaded_file.filename.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(uploaded_file)
                else:  
                    df = pd.read_csv(uploaded_file)

                csv_file_path = 'converted_file.csv'
                df.to_csv(csv_file_path, index=False)

    return render_template('index.html')

@app.route('/ask_pdf', methods=['POSt','GET'])
def question():
    
    pdf_docs = ['uploaded_pdf.pdf']
    raw_text = get_pdf_text(pdf_docs)
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)
    conversation_chain = get_conversation_chain(vectorstore)

    if request.method == 'POST':
        user_question = request.form['question']
        print(user_question)
        
        response = conversation_chain({'question': user_question})
        print(response)
        response_text = response['answer']
        print("pdf resposne>>>>>>",response_text)

        bg_thread = Thread(target=background_speak, args=(response_text,))
        bg_thread.start()

        return jsonify({"response_text":response_text})

    return jsonify({"error": "No file uploaded"})

@app.route('/ask_csv', methods=['POST'])
def upload_excel():
    if request.method == 'POST':
        user_question = request.form['question']

        csv = ["converted_file.csv"]

        agent = create_csv_agent(
            OpenAI(temperature=0),
            csv,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        )

        response_text = agent.run(user_question)
        print(response_text)

        bg_thread = Thread(target=background_speak, args=(response_text,))
        bg_thread.start()

        return jsonify({"response_text":response_text})

    return jsonify({"error": "No file uploaded"})

@app.route('/gpt_3', methods = ['POST'])
def gpt3():
    question = request.form['question']
    print(question)

    conversation_with_summary = ConversationChain(
    llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0), 
    memory=ConversationBufferWindowMemory(k=3), 
    verbose=True
    )

    response_text = conversation_with_summary.predict(input=question)
    print("GPT 3>>>>>>>",response_text)
    bg_thread = Thread(target=background_speak, args=(response_text,))
    bg_thread.start()

    return jsonify({"response_text":response_text})

@app.route('/gpt_4', methods = ['POST'])
def gpt4():
    question = request.form['question']
    print(question)
    conversation_with_summary = ConversationChain(
    llm=ChatOpenAI(model="gpt-4", temperature=0), 
    memory=ConversationBufferWindowMemory(k=3), 
    verbose=True
    )

    response_text = conversation_with_summary.predict(input=question)
    print("GPT 4",response_text)
    bg_thread = Thread(target=background_speak, args=(response_text,))
    bg_thread.start()

    return jsonify({"response_text":response_text})

    

if __name__ == '__main__':
    app.run(debug=True)