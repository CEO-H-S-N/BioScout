import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if HF_API_KEY is None:
    raise ValueError("HUGGINGFACE_API_KEY not found in .env file!")

# 🔍 IMAGE MODEL: BEiT-Large
def identify_species_with_huggingface(image_file):
    API_URL = "https://api-inference.huggingface.co/models/microsoft/beit-large-patch16-224"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/octet-stream"
    }
    image_file.seek(0)
    image_bytes = image_file.read()

    response = requests.post(API_URL, headers=headers, data=image_bytes)
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and 'label' in result[0]:
            return result[0]['label']
    print("API Error:", response.status_code, response.text)
    return "Unknown Species"

# 🧠 LLM MODEL: Mistral-7B-Instruct
def query_llm_with_context(query, context):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:",
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        output = response.json()
        if isinstance(output, list) and "generated_text" in output[0]:
            return output[0]["generated_text"].split("Answer:")[-1].strip()
    print("API Error:", response.status_code, response.text)
    return "Sorry, I couldn't generate an answer."
