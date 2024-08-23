from typing import Dict, List, Tuple, Union
from datetime import datetime
from mage_ai.data_preparation.variable_manager import set_global_variable


import numpy as np
from elasticsearch import Elasticsearch

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def elasticsearch(
    documents: List[Dict[str, Union[Dict, List[int], np.ndarray, str]]], *args, **kwargs,
):
    """
    Exports document data to an Elasticsearch database.
    """

    connection_string = kwargs.get('connection_string', 'http://localhost:9200')
    #index_name = kwargs.get('index_name', 'documents')
    index_name_prefix = kwargs.get('index_name', 'documents')
    current_time = datetime.now().strftime("%Y%m%d_%M%S")
    index_name = f"{index_name_prefix}_{current_time}"
    set_global_variable('crepuscular_nebula', 'index_name', index_name)
    print("index name:", index_name)
    number_of_shards = kwargs.get('number_of_shards', 1)
    number_of_replicas = kwargs.get('number_of_replicas', 0)
    vector_column_name = kwargs.get('vector_column_name', 'embedding')

    dimensions = kwargs.get('dimensions')
    if dimensions is None and len(documents) > 0:
        document = documents[0]
        dimensions = len(document.get(vector_column_name) or [])

    es_client = Elasticsearch(connection_string)

    print(f'Connecting to Elasticsearch at {connection_string}')

    index_settings = dict(
        settings=dict(
            number_of_shards=number_of_shards,
            number_of_replicas=number_of_replicas,
        ),
        mappings=dict(
            properties=dict(
                text=dict(type='text'),
                section=dict(type='text'),
                question=dict(type='text'),
                course=dict(type='keyword'),
                document_id=dict(type='keyword')
            ),
        ),
    )

    if not es_client.indices.exists(index=index_name):
        es_client.indices.create(index=index_name)
        print('Index created with properties:', index_settings)
        print('Embedding dimensions:', dimensions)

    print(f'Indexing {len(documents)} documents to Elasticsearch index {index_name}')
    
    countx = len(documents)
    # Track last reported progress
    last_reported_progress = 0
    for idx, document in enumerate(documents):
        # Calculate progress percentage
        progress = (idx + 1) / countx * 100

        # Update progress every 10%
        if int(progress // 10) * 10 > last_reported_progress:
            last_reported_progress = int(progress // 10) * 10
            print(f"Progress: {last_reported_progress}%")

        #print(f'Indexing document {document["document_id"]}')
        es_client.index(index=index_name, document=document)
    print(document) 