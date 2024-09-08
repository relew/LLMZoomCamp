# Philosophy Assitant

## Problem Description

In an increasingly complex world, understanding philosophical principles can offer valuable insights into personal growth, decision-making, and well-being. However, accessing and interpreting philosophical wisdom from diverse traditions like Stoicism and Zen can be challenging for many people. 

The Philosophy Assistant LLM Model addresses these challenges by providing a digital assistant that delivers:

- **Accessible Philosophical Guidance:** Many individuals struggle to interpret and apply ancient philosophical teachings to modern life. This LLM model offers accessible and actionable insights grounded in Stoic and Zen philosophies, making these teachings more relevant and understandable.

- **Contextualized Answers:** Traditional philosophical texts can be dense and difficult to navigate. The model simplifies this by providing clear, contextually relevant answers to user questions, derived from established philosophical principles.

- **Enriched Understanding through Quotes:** By including relevant quotes from notable philosophers, the model not only answers questions but also connects users with the original philosophical sources, enhancing their understanding and engagement.

- **Educational Value:** The explanations of quotes and principles promote deeper learning and reflection, helping users integrate philosophical concepts into their daily lives and decision-making processes.

- **Personalized Philosophy Learning:** Users can explore Stoic and Zen philosophies interactively, receiving personalized responses that cater to their specific questions and interests, fostering a more engaging and tailored learning experience.

In essence, the Philosophy Assistant LLM Model serves as a bridge between ancient philosophical wisdom and contemporary needs, making profound philosophical teachings more accessible, relevant, and impactful in today's world.


## Dataset Description

The dataset for the Philosophy Assistant LLM Model consists of a collection of question-answer pairs categorized by philosophical figures and ideologies. The dataset is structured as follows:

- **Category:** The philosopher or philosophical school associated with each entry, such as al-Kindi, Alexander of Aphrodisias, or Stoicism.
- **Question:** Specific philosophical queries related to the category, addressing various aspects of philosophical thought and historical context.
- **Answer:** Detailed responses that provide insights into the philosophical topics covered in the questions.
- **Ideology:** The philosophical ideology or tradition relevant to the question and answer, such as Stoicism.

This dataset serves as the foundational knowledge base for the model, enabling it to provide accurate and contextually rich answers based on historical and philosophical content.


## Running it

## Ingestion

## Rag flow

For the code for basic rag flow, you can check the [notebooks/step1_basic_rag_flow.ipynb](notebooks/step1_basic_rag_flow.ipynb) notebook.

## Retrival Evaluation

For the code for evaluating the system, you can check the [notebooks/step3_retrieval_evaluation.ipynb](notebooks/step3_retrieval_evaluation.ipynb) notebook.

Basic approach - using minsearch without any boosting gave the following metric(num_results=5):
{'hit_rate': 0.8043902439024391, 'mrr': 0.6790121951219511}

after basic input field param weight hypertuning - results are the followings:
{'hit_rate': 0.9185365853658537, 'mrr': 0.7592213511420829}

## RAG evaluation

For the code for RAG evaluation, you can check the [notebooks/step4_rag_evaluation.ipynb](notebooks/step4_rag_evaluation.ipynb) notebook.

Cosine Similarity

Answer -> Question -> Answer Cosine Similarity: 0.82

LLM as a Judge

Answer -> Question -> Answer: 149/150(99%) RELEVANT

Question -> Answer: 145/150(97%) RELEVANT



## Monitoring

