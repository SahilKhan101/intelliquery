"""Quick test to verify Google API key is working"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
    exit(1)

print(f"✓ Found API key: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print("✓ Testing API connection...")
    response = model.generate_content("Say 'Hello, API is working!'")
    
    print(f"✓ SUCCESS! Response: {response.text}")
    print("\n✅ Your API key is valid and working!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\n🔑 Your API key is INVALID or REVOKED. Please:")
    print("1. Go to https://aistudio.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Update GOOGLE_API_KEY in .env file")
    print("4. Restart the Streamlit app")
