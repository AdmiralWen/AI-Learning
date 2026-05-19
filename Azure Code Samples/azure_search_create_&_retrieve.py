import os
from typing import List, Dict
from openai import AzureOpenAI

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchFieldDataType,
    SearchResourceEncryptionKey,
    CorsOptions,
    SearchIndex,
    SimpleField
)

# First run 'az login' in bash (terminal), then run the following:
from azure.identity import DefaultAzureCredential
default_credential = DefaultAzureCredential()
token = default_credential.get_token("https://cognitiveservices.azure.com/.default")

# Define credentials:
acs_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
acs_credentials = default_credential

encryption_key = SearchResourceEncryptionKey(
    vault_uri = os.getenv('AZURE_SEARCH_ENCRYPTION_VAULT_URI'),
    key_name = os.getenv('AZURE_SEARCH_ENCRYPTION_KEY_NAME'),
    key_version = os.getenv('AZURE_SEARCH_ENCRYPTION_KEY_VERSION')
)

# Azure Search client:
admin_client = SearchIndexClient(endpoint=acs_endpoint, credential=acs_credentials)

# Define CORS options:
cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)

# Define Text search fields:
fields = [
    SimpleField(name="PermId", type=SearchFieldDataType.String, key=True),
    SimpleField(name="Name", type=SearchFieldDataType.String, filterable=True, facetable=True)
]

# Create the search index with the semantic, tokenizer, and filter settings
index = SearchIndex(
    name = 'test_index_creation',
    fields = fields,
    cors_options = cors_options,
    encryption_key = encryption_key
)
result = admin_client.create_or_update_index(index)
print(f'{result.name} created.')


#########################


from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

def azure_search_text(
    search_client: SearchClient,
    query: str,
    query_type = 'simple',
    search_mode = 'any',
    search_fields: List = None,
    scoring_profile: str = None,
    filter: str = None,
    top_k: int = 5,
    select: List[str] = None
) -> List[Dict]:
    '''
    Implements text search given an Azure SearchClient, with optional scoring profiles.

    Args:
        search_client (SearchClient): An authenticated Azure Search client object.
        query (str): The user query to search.
        query_type ('simple' or 'full'): Parameter for which type of query syntax to use.
        search_mode ('simple' or 'full'): Parameter for the search mode to use.
        search_fields (List): An optional list of searchable fields to use for the search.
        scoring_profile (str): Name of the scoring profile to use, optional.
        filter (str): The filter string to be applied, in OData $filter syntax.
        top_k (int): Number of search results to retrieve.
        select (List): An optional list of fields to retrieve for each search result.

    Returns:
        results (List): List of retrieved search results.
    '''
    search_iter = search_client.search(
        search_text = query,
        query_type = query_type,
        search_mode = search_mode,
        search_fields=search_fields,
        scoring_profile=scoring_profile,
        filter=filter,
        top=top_k,
        select=select
    )
    results = [r for r in search_iter]

    return results


def azure_search_hybrid(
    search_client: SearchClient,
    oai_client: AzureOpenAI,
    query: str,
    text_search_fields: List[str],
    vec_search_fields: List[str],
    query_type = 'simple',
    search_mode = 'any',
    scoring_profile: str = None,
    filter: str = None,
    top_k: int = 5,
    select: List[str] = None
) -> List[Dict]:
    '''
    Implements hybrid search given an Azure SearchClient, with optional scoring profiles.

    Args:
        search_client (SearchClient): An authenticated Azure Search client object.
        oai_client (AzureOpenAI): An Azure OpenAI client for embedding generation.
        query (str): The user query to search.
        text_search_fields (List): A list of searchable fields to use for the TEXT search.
        vec_search_fields (List): A list of searchable fields to use for the VECTOR search.
        query_type ('simple' or 'full'): Parameter for which type of query syntax to use.
        search_mode ('simple' or 'full'): Parameter for the search mode to use.
        scoring_profile (str): Name of the scoring profile to use, optional.
        filter (str): The filter string to be applied, in OData $filter syntax.
        top_k (int): Number of search results to retrieve.
        select (List): An optional list of fields to retrieve for each search result.

    Returns:
        results (List): List of retrieved search results.
    '''
    # Embed query:
    oai_response = oai_client.embeddings.create(input=[query], model='text_embedding_3_small')
    query_vector = oai_response.data[0].embedding

    # Vector search list for hybrid search:
    vector_search_list = [
        VectorizedQuery(
            k_nearest_neighbors=top_k,
            fields=f,
            vector=query_vector
        )
        for f in vec_search_fields
    ]

    search_iter = search_client.search(
        search_text=query,
        search_fields=text_search_fields,
        vector_queries=vector_search_list,
        query_type = query_type,
        search_mode = search_mode,
        scoring_profile=scoring_profile,
        filter=filter,
        top=top_k,
        select=select
    )
    results = [r for r in search_iter]

    return results
