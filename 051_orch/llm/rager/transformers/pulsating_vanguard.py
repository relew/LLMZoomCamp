import hashlib
from mage_ai.data_preparation.decorators import transformer

@transformer
def transform(data, *args, **kwargs):
    # You can print the type of data to verify the structure
    print(type(data))

    documents = []

    def generate_document_id(doc):
        combined = f"{doc['course']}-{doc['question']}-{doc['text'][:10]}"
        hash_object = hashlib.md5(combined.encode())
        hash_hex = hash_object.hexdigest()
        document_id = hash_hex[:8]
        return document_id

    for doc in data['documents']:
        doc['course'] = data['course']
        # previously we used just "id" for document ID
        doc['document_id'] = generate_document_id(doc)
        documents.append(doc)

    print(len(documents))
    print(type(data))
    
    data['documents'] = documents  # Optionally update the original data with transformed documents

    return data

