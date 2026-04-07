import os
import json
from google import genai
from dotenv import load_dotenv
from datetime import date

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

today = date.today().strftime("%d-%m-%Y")

def extract_details(user_text: str):
    prompt = f"""
You are an AI assistant for scheduling interviews.
Today's date is {today}.

Extract structured information from the user input.

Return ONLY valid JSON in this exact format:
{{
  "candidate_name": "",
  "datetime": ""
}}

Rules:
- candidate_name: full name of the candidate exactly as mentioned
- datetime: convert to readable format like "April 8, 2026 at 5:00 PM"
- If today is needed, use context clues like "tomorrow" or "next Monday"
- Return ONLY the JSON object, nothing else

User input:
{user_text}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )

        raw_text = response.text.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw_text)
        return data

    except Exception as e:
        print("LLM Error:", e)
        return None