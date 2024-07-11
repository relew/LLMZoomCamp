import streamlit as st
import time  # for simulating loading
from elasticsearch import Elasticsearch
from tqdm import tqdm
from openai import OpenAI
import os,sys

def check_similarities(user_question, index_name = "llm-course-questions" , max_results = 5):
    search_query = {
        "size": max_results,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": user_question,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "llm-course-questions"
                    }
                }
            }
        }
    }

    response = es.search(index=index_name, body=search_query)
    documents = [hit["_source"] for hit in response['hits']['hits']]
    return documents
    
def build_prompt(query, search_results):
    prompt_template = """
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

    context = ""
    
    for doc in search_results:
        context = context + f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

def llm(prompt):
    response = client.chat.completions.create(
        model='phi3',
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def rag(question,search_engine):
    query = question
    index_name = search_engine
    search_results = check_similarities(query,index_name)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer

es = Elasticsearch("http://localhost:9200")

client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)

# # Define your 'rag' function here
# def rag(question, search_engine):
#     # Replace with your function logic (e.g., API calls, processing)
#     time.sleep(3)  # Simulating some processing time
#     return f"Question: {question}, Search Engine: {search_engine}"

# Streamlit app layout
def main():
    st.title('Question Answering System')
    
    # Input box for question
    question = st.text_input('Enter your question:')
    
    # Selectbox for search engines
    search_engine = st.selectbox('Select a search engine:', ['streamlit_w_dogs', 'llm-course-questions', 'Yahoo'])
    
    # Button to trigger 'rag' function
    if st.button('Ask'):
        # Show loading indicator
        with st.spinner('Searching...'):
            # Call your 'rag' function
            result = rag(question, search_engine)
            # Display result after function completes
            st.write(result)

if __name__ == '__main__':
    main()
