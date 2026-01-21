print("Starting model list script...")
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env from current directory explicitly
load_dotenv(os.path.abspath('.env'))

api_key = os.getenv('GOOGLE_API_KEY')
print(f"API Key found: {'Yes' if api_key else 'No'}")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
