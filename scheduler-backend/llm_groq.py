import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_details(user_text: str):
    prompt = f"""
You are an AI assistant for scheduling interviews.

Extract structured information from the user input.

Return ONLY valid JSON in this exact format:
{{
  "candidate_name": "",
  "datetime": ""
}}

Rules:
- candidate_name: full name of the candidate exactly as mentioned
- datetime: convert to readable format like "April 8, 2026 at 5:00 PM"
- Return ONLY the JSON object, nothing else

User input:
{user_text}
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        raw_text = response.choices[0].message.content.strip()
        return json.loads(raw_text)

    except Exception as e:
        print("LLM Error:", e)
        return None