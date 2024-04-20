# -*- coding: utf-8 -*-
"""QA Generation System.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JRIs3y5EGl8-Bxtf9crm_MoHRQywyuaK
"""

# !pip install langchain
# !pip install PyPDF2
# !pip install pypdf
# !pip install tiktoken
# !pip install openai
# !pip install faiss-gpu

from langchain.chat_models import ChatOpenAI
from langchain.chains import QAGenerationChain
from langchain.text_splitter import TokenTextSplitter
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import RetrievalQA
from langchain.chains import LLMChain
from openai import OpenAIError
import os
import re
import json
import time
from PyPDF2 import PdfReader
import csv

# from google.colab import files

# uploaded = files.upload()

def generate_true_false_questions(text):
    """
    Generate true/false questions based on the provided text.

    Args:
        text (str): The text content to base the questions on.

    Returns:
        list: A list of generated true/false questions.
    """
    # Initialize a language model for question generation
    llm_ques_gen = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")

    # Define the prompt template for true/false questions
    true_false_prompt_template = """
    You are an expert at creating true/false questions based on the provided text.
    Your goal is to test the knowledge of coders or programmers on the content below:

    ------------
    {text}
    ------------

    Create true/false questions that will assess understanding.
    Ensure questions are clear and relevant.

    QUESTIONS:
    """

    # Create a prompt template with the specified input variable
    prompt = PromptTemplate(input_variables=["text"], template=true_false_prompt_template)

    try:
        llmChain = LLMChain(llm=ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo"), prompt=prompt)
        # Generate questions using the language model
        questions = llmChain.run(text)

        # Parse and format the generated questions
        ques = []
        questions = re.findall(r'(\d+)\.\s+(.*)', questions)
        for number, question in questions:
            ques.append(f"{number}. {question}")

        return ques
    except OpenAIError as e:
        wait_time = 20
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
        generate_true_false_questions(text)



    return []

def generate_multiple_choice_questions(text):
    """
    Generate multiple-choice questions based on the provided text.

    Args:
        text (str): The text content to base the questions on.

    Returns:
        list: A list of generated multiple-choice questions.
    """
    # Define the prompt template for multiple-choice questions
    prompt_template = """
    You are preparing multiple-choice questions based on the following text chunk:
    ------------
    {text}
    ------------

    Generate multiple-choice questions that cover important concepts.
    Provide clear and relevant options.

    QUESTIONS:
    """

    # Create a prompt template with the specified input variable
    prompt = PromptTemplate(input_variables=["text"], template=prompt_template)
    # Initialize an LLMChain for question generation
    try:
        llmChain = LLMChain(llm=ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo"), prompt=prompt)

        # Generate questions using the language model
        questions = llmChain.run(text)
        # Split generated questions into blocks and format them
        question_blocks = questions.strip().split('\n\n')
        question_array = []
        for block in question_blocks:
            lines = block.strip().split('\n')
            question_number, question_content = lines[0].split('. ', 1)
            options = ' '.join(f"{line.strip()}" for line in lines[1:])
            formatted_question = f"{question_number}. {question_content} {options}"
            question_array.append(formatted_question)
        print("QA", question_array)
        return question_array
    except OpenAIError as e:
        wait_time = 20
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
        generate_multiple_choice_questions(text)
    
    return []

def generate_one_word_answer_questions(text):
    """
    Generate one-word answer questions based on the provided text.

    Args:
        text (str): The text content to base the questions on.

    Returns:
        list: A list of generated one-word answer questions.
    """
    # Define the prompt template for one-word answer questions
    prompt_template = """
    You are preparing questions that will have one word answers only based on the following text chunk:
    ------------
    {text}
    ------------

    Generate one-word answer questions that target key information.

    QUESTIONS:
    """

    # Create a prompt template with the specified input variable
    prompt = PromptTemplate(input_variables=["text"], template=prompt_template)

    try:
        llmChain = LLMChain(llm=ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo"), prompt=prompt)

        # Generate questions using the language model
        questions = llmChain.run(text)

        # Split generated questions into a list
        questions = questions.split('\n')
        return questions
    except OpenAIError as e:
        wait_time = 20
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
        generate_one_word_answer_questions(text)

    return []

def process_text_and_generate_questions(text):

    splitter = TokenTextSplitter(model_name='gpt-3.5-turbo', chunk_size=10000, chunk_overlap=200)
    text_chunks = splitter.split_text(text)

    all_questions = {
        "true_false": [],
        "multiple_choice": [],
        "one_word_answer": []
    }

    for chunk in text_chunks:
        if chunk.strip():
            # Generate questions for each chunk and append to respective lists
            all_questions["true_false"] = generate_true_false_questions(chunk)
            all_questions["multiple_choice"] = generate_multiple_choice_questions(chunk)
            all_questions["one_word_answer"] = generate_one_word_answer_questions(chunk)

    return all_questions

def file_processing(question_gen):

    # Load data from PDF
    # loader = PyPDFLoader(file_path)
    # data = loader.load()

    # question_gen = ''

    # for page in data:
    #     question_gen += page.page_content

    splitter_ques_gen = TokenTextSplitter(
        model_name = 'gpt-3.5-turbo',
        chunk_size = 10000,
        chunk_overlap = 200
    )

    chunks_ques_gen = splitter_ques_gen.split_text(question_gen)

    document_ques_gen = [Document(page_content=t) for t in chunks_ques_gen]

    splitter_ans_gen = TokenTextSplitter(
        model_name = 'gpt-3.5-turbo',
        chunk_size = 1000,
        chunk_overlap = 100
    )


    document_answer_gen = splitter_ans_gen.split_documents(
        document_ques_gen
    )

    return document_ques_gen, document_answer_gen

def generate_true_false_answers(text, answer_generation_chain):
    """
    Generate a true/false answer based on the provided text using a language model.

    Args:
        text (str): The text containing the statement to answer.
        llm_model: The language model used for generating answers.

    Returns:
        str: The generated true/false answer (either 'true' or 'false').
    """

    try:
        result = answer_generation_chain({"query": text + 'Only Answer.'})
        # Clean up the generated answer (convert to lowercase and strip whitespace)
        cleaned_answer = result['result'].strip().lower()
        return cleaned_answer
    except OpenAIError as e:
        wait_time = 20
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
        generate_true_false_answers(text, answer_generation_chain)


    return ''

def generate_multiple_choice_answers(text, answer_generation_chain):
    """
    Generate a multiple-choice answer based on the provided text using a language model.

    Args:
        text (str): The text containing the multiple-choice question.
        llm_model: The language model used for generating answers.

    Returns:
        str: The generated multiple-choice answer (e.g., 'A', 'B', 'C', etc.).
    """
    try:
        result = answer_generation_chain({"query": text + 'Please select the correct option (A, B, C, etc.) for the following question. Only Answer.'})
        cleaned_answer = result['result'].strip().upper()
        return cleaned_answer
    except OpenAIError as e:
        wait_time = 20
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
        generate_multiple_choice_answers(text, answer_generation_chain)


    return ''

def generate_one_word_answers(text, answer_generation_chain):
    """
    Generate a one-word answer based on the provided text using a language model.

    Args:
        text (str): The text containing the question requiring a one-word answer.
        llm_model: The language model used for generating answers.

    Returns:
        str: The generated one-word answer.
    """
    try:
        result = answer_generation_chain({"query": text + 'Please provide a one-word answer to the following question. Only Answer.'})
        # Clean up the generated answer (convert to uppercase and strip whitespace)
        cleaned_answer = result['result'].strip().lower()
        return cleaned_answer
    except OpenAIError as e:
        wait_time = 20
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
        generate_one_word_answers(text, answer_generation_chain)


    return cleaned_answer

def generate_ans_for_generated_ques(generated_questions, pdf_text):
    """
    Generate answers for the generated questions and write them to a CSV file.

    Args:
        generated_questions (dict): A dictionary containing lists of generated questions.

    Returns:
        None
    """
    document_ques_gen, document_answer_gen = file_processing(pdf_text)


    embeddings = OpenAIEmbeddings()

    vector_store = FAISS.from_documents(document_answer_gen, embeddings)

    llm_answer_gen = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo")

    answer_generation_chain = RetrievalQA.from_chain_type(llm=llm_answer_gen,
                                                chain_type="stuff",
                                                retriever=vector_store.as_retriever())


    # Dictionary to store question-answer mappings
    question_answer_mapping = {}

    # Generate answers for true/false questions
    # Add section header for true/false questions and answers
    question_answer_mapping["=== TRUE/FALSE QUESTIONS ==="] = "=== ANSWERS BELOW ==="
    for question in generated_questions["true_false"]:
        generated_answer = generate_true_false_answers(question, answer_generation_chain)
        question_answer_mapping[question] = generated_answer
    # print(question_answer_mapping)


    # # Add section header for multiple-choice questions and answers
    question_answer_mapping["=== MULTIPLE CHOICE QUESTIONS ==="] = "=== ANSWERS BELOW ==="
    # Generate answers for multiple-choice questions
    for question in generated_questions["multiple_choice"]:
        generated_answer = generate_multiple_choice_answers(question, answer_generation_chain)
        question_answer_mapping[question] = generated_answer


    # Add section header for one-word answer questions and answers
    question_answer_mapping["=== ONE-WORD ANSWER QUESTIONS ==="] = "=== ANSWERS BELOW ==="
    # Generate answers for one-word answer questions
    for question in generated_questions["one_word_answer"]:
        generated_answer = generate_one_word_answers(question, answer_generation_chain)
        question_answer_mapping[question] = generated_answer

    print(question_answer_mapping)


    return question_answer_mapping
