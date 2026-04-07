import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("\n--- YOUR AVAILABLE MODELS ---")
try:
    for model in client.models.list():
        # Filter for models that can actually chat (generateContent)
        if "generateContent" in model.supported_methods:
            print(f"✅ {model.name}")
except Exception as e:
    print(f"❌ Error fetching models: {e}")
