from typing import Dict, List, Union
import numpy as np
import json
from elasticsearch import Elasticsearch, exceptions
from mage_ai.data_preparation.variable_manager import get_global_variable

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


question_sample = "When is the next cohort?"
course_sample = "llm-zoomcamp-v2"

@data_loader
def search(*args, **kwargs) -> List[Dict]:
    """
    query_embedding: Union[List[int], np.ndarray]
    """
    
    connection_string = kwargs.get('connection_string', 'http://localhost:9200')
    #index_name = kwargs.get('index_name', 'documents')
    index_name = get_global_variable('crepuscular_nebula', 'index_name')
    print("Index name:", index_name)
    source = kwargs.get('source', "cosineSimilarity(params.query_vector, 'embedding') + 1.0")
    top_k = kwargs.get('top_k', 1)
    #chunk_column = kwargs.get('chunk_column', 'content')

    question = None
    course = course_sample
    if len(args):
        question = args[0]
        if len(args) > 1:
            course = args[1]

    if not question:
        question = question_sample

    # Construct the query
    script_query = {
        "size": 1,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": question_sample,
                            "fields": ["question^3", "text", "section"],
                            "type": "best_fields"
                        }
                    }
                ],
                "filter": [
                    {
                        "term": {
                            "course.keyword": course_sample  # Use `.keyword` for exact match on keyword fields
                        }
                    }
                ]
            }
        }
    }
    print("Sending script query:", script_query)
    es_client = Elasticsearch(connection_string)
    
    try:
        # Perform the search query
        response = es_client.search(
            index=index_name,
            body=script_query
        )

        # Format and return the result documents
        result_docs = [hit['_source'] for hit in response['hits']['hits']]
        
        # Pretty print the results
        print("Search results:")
        print(json.dumps(result_docs, indent=2))  # Pretty-print with indentation

        return result_docs

    
    except exceptions.BadRequestError as e:
        print(f"BadRequestError: {e.info}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
