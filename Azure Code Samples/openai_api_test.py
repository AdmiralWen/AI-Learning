import openai
import os
from azure.identity import DefaultAzureCredential

# In terminal type `az login` to login, then login on your browser popup, then select an environment in the terminal (usually 1):
default_credential = DefaultAzureCredential()
token = default_credential.get_token("https://cognitiveservices.azure.com/.default")

# Create OpenAI client:
client = openai.AzureOpenAI(
    api_key = token.token,
    api_version = os.getenv('AZURE_OPENAI_API_VERSION'),
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
)

# Test embeddings generation:
test_str = 'The Hagia Sophia is a domed monument built as a cathedral and is now a museum in Istanbul, Turkey.'
oai_response = client.embeddings.create(input = [test_str], model='text-embedding-3-small')
print(len(oai_response.data[0].embedding))
oai_response.data[0].embedding

# Test chat completion:
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
        {"role": "user", "content": "Who were the founders of Microsoft?"}
    ]
)