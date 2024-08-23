from typing import List, Tuple

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def delimiter_chunker(document_data: Tuple[str, str], *args, **kwargs) -> List[Tuple[str, str, str]]:
    """
    Template for delimiter-based chunking of a document.

    Args:
        document_data (Tuple[str, str]): Tuple containing document_id and document_content.
        delimiter (str, optional): The delimiter to use for chunking from kwargs.

    Returns:
        List[Tuple[str, str, str]]: List of tuples containing document_id, document_content, and chunk_text.
    """
    document_id, document_content = document_data
    delimiter = kwargs.get('delimiter', '\n\n')  # Default delimiter

    chunks = document_content.split(delimiter)
    chunked_data = [(document_id, document_content, chunk) for chunk in chunks]

    return chunked_data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'