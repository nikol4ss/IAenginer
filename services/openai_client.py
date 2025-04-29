from openai import OpenAI
import os

def openai_client_authentication(key: str):
    client = OpenAI(api_key=key)

    return client

openai_key = os.getenv('OPENAI_API_KEY')

print(openai_client_authentication(openai_key))
