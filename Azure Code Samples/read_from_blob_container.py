from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

storage_account_name = os.getenv('AZURE_STORAGE_CONTAINER_ACCOUNT_NAME')
container_name = 'test-container'
blob_name = 'sample_data/'

blob_client = BlobClient(
    account_url = f'https://{storage_account_name}.blob.core.windows.net',
    container_name = container_name,
    blob_name = blob_name,
    credential = os.getenv('AZURE_STORAGE_CONTAINER_KEY')
)

blob_data = blob_client.download_blob().readall()