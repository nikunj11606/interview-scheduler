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
IMPORTANT: Today's date is {today} (Date-Month-Year). All relative terms like 'tomorrow', 'today', or 'next Monday' MUST be calculated from this date.

Extract structured information from the user input.

Return ONLY valid JSON in this exact format:
{{
  "candidate_name": "Full Name",
  "datetime": "Clean Datetime String"
}}

Rules:
1. candidate_name: full name of the candidate exactly as mentioned.
2. datetime: convert to a clear format like "April 8, 2026 at 5:00 PM".
3. Accuracy: Ensure the day and month are correct based on {today}.
4. Strictness: Return ONLY the JSON object. Do not include any extra text.

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

        # Robust JSON finding: locate the first '{' and last '}'
        start_idx = raw_text.find('{')
        end_idx = raw_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            json_str = raw_text[start_idx:end_idx + 1]
            data = json.loads(json_str)
            return data
        
        return None

    except Exception as e:
        print("LLM Error:", e)
        return None