import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(override=True)
key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=key)
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)
