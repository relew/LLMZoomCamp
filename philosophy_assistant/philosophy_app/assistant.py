import os
import time
import json
import minsearch as minsearch
import pandas as pd
from openai import OpenAI
from sentence_transformers import SentenceTransformer


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1/")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

def print_log(message):
    print(message, flush=True)

# Load the documents
df = pd.read_csv("stoic_zen_document.csv")
df.insert(0, 'id', df.index)
documents = df.to_dict(orient="records")
print("Length of the documents:", len(documents))

# Initializing the MinSearch index
index = minsearch.Index(
    text_fields=["category", "question", "answer"],
    keyword_fields=["id", "ideology"]
)

# Fit the index with the documents
index.fit(documents)

# Initialize OpenAI client
openai_client = OpenAI()
ollama_client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")

# Function to search with MinSearch
def minsearch_search(query, ideology):
    boost = {'question': 3.0, 'category': 0.5}
    results = index.search(
        query=query,
        filter_dict={'ideology': ideology},
        boost_dict=boost,
        num_results=5
    )
    return results

# Function to call the LLM (OpenAI API)
def llm(prompt, model_choice):
    start_time = time.time()
    if model_choice.startswith('ollama/'):
        response = ollama_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    elif model_choice.startswith('openai/'):        
        response = openai_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    else:
        raise ValueError(f"Unknown model choice: {model_choice}")
    
    end_time = time.time()
    response_time = end_time - start_time
    
    return answer, tokens, response_time

# Function to build the prompt for the LLM
def build_prompt(query, search_results):
    start_time = time.time()
    prompt_template = """
    You're a philosophy teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
    Use only the facts from the CONTEXT when answering the QUESTION. Provide a real life quote proving your point, stating the author as well.
    
    QUESTION: {question}
    
    CONTEXT: 
    {context}
    """.strip()

    entry_template = """
    category: {category}
    question: {question}
    answer: {answer}
    ideology: {ideology}
    """.strip()

    # Build the context from the search results
    context = "\n\n".join([entry_template.format(**doc) for doc in search_results])
    
    # Return the final prompt
    return prompt_template.format(question=query, context=context).strip()

def calculate_openai_cost(model_choice, tokens):
    openai_cost = 0

    if model_choice == 'openai/gpt-3.5-turbo':
        openai_cost = (tokens['prompt_tokens'] * 0.0015 + tokens['completion_tokens'] * 0.002) / 1000
    elif model_choice in ['openai/gpt-4o', 'openai/gpt-4o-mini']:
        openai_cost = (tokens['prompt_tokens'] * 0.03 + tokens['completion_tokens'] * 0.06) / 1000

    return openai_cost


def evaluate_relevance(question, answer):
    prompt_template = """
    You are an expert evaluator for a philosophical Retrieval-Augmented Generation (RAG) system.
    Your task is to analyze the relevance of the generated answer to the given philosophical question.
    Based on the relevance of the generated answer, you will classify it
    as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

    Here is the data for evaluation:

    Question: {question}
    Generated Answer: {answer}

    Please analyze the philosophical depth, context, and relevance of the generated answer in relation to the question,
    and provide your evaluation in parsable JSON without using code blocks:

    {{
      "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
      "Explanation": "[Provide a brief explanation for your evaluation based on philosophical reasoning]"
    }}
    """.strip()

    # Construct the prompt with the question and answer
    prompt = prompt_template.format(question=question, answer=answer)

    # Call the LLM to perform the evaluation
    evaluation, tokens, _ = llm(prompt, 'openai/gpt-4o-mini')

    # Attempt to parse the evaluation result as JSON
    try:
        json_eval = json.loads(evaluation)
        return json_eval['Relevance'], json_eval['Explanation'], tokens
    except json.JSONDecodeError:
        return "UNKNOWN", "Failed to parse evaluation", tokens

def get_answer(query, ideology, model_choice, search_type):
    
    if search_type == "Text":
        search_results = minsearch_search(query, ideology)

    else:
        print("search type problem")
       
    prompt = build_prompt(query, search_results)
    answer, tokens, response_time = llm(prompt, model_choice)
    
    relevance, explanation, eval_tokens = evaluate_relevance(query, answer)

    openai_cost = calculate_openai_cost(model_choice, tokens)
 
    return {
        'answer': answer,
        'response_time': response_time,
        'relevance': relevance,
        'relevance_explanation': explanation,
        'model_used': model_choice,
        'prompt_tokens': tokens['prompt_tokens'],
        'completion_tokens': tokens['completion_tokens'],
        'total_tokens': tokens['total_tokens'],
        'eval_prompt_tokens': eval_tokens['prompt_tokens'],
        'eval_completion_tokens': eval_tokens['completion_tokens'],
        'eval_total_tokens': eval_tokens['total_tokens'],
        'openai_cost': openai_cost
    }