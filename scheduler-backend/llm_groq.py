import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process_request(user_text: str, data_summary: str, history: list):
    today = datetime.now().strftime("%B %d, %Y")
    
    # 1. Start with the system instructions
    groq_messages = [
        {"role": "system", "content": f"You are an AI Interview Assistant. Today's Date: {today}"}
    ]

    # 2. Add the conversation history (Memory)
    for msg in history:
        # Convert frontend 'bot' role to Groq 'assistant' role
        role = "assistant" if msg["role"] == "bot" else "user"
        groq_messages.append({"role": role, "content": msg["text"]})

    # 3. Add the current prompt with the new data summary
    prompt = f"""
CURRENT SYSTEM DATA:
{data_summary}

TASK:
Identify the user's intent and extract details if necessary.
You can handle three intents:
1. SCHEDULE: User wants to book a new interview.
2. CANCEL: User wants to cancel an existing interview.
3. QUERY: User is asking a question, chatting, or making a request about the data.

Rules:
- If SCHEDULE: Extract 'candidate_name' and 'datetime'.
- If CANCEL: Identify 'candidate_name'.
- If QUERY: Don't add technical words like pending, None in reply. GIVE MORE HUMAN LIKE ANSWER based on CURRENT SYSTEM DATA.
- Readiness Rule: If the user wants to SCHEDULE, you must have BOTH a valid 'candidate_name' AND a 'datetime'. If they want to CANCEL, you must have a valid 'candidate_name'. If ANY required information is missing from the chat history, you MUST set "readiness" to "MISSING_INFO", change intent to "QUERY", and ask the user for the missing details. Otherwise, set "readiness" to "READY".
- Ambiguity: If a user mentions a name that matches multiple candidates (e.g. 'Arjun'), do not schedule. Set "readiness" to "MISSING_INFO", intent to QUERY, and ask for clarification WITH THE LIST OF POSSIBLE NAMES. YOU MUST NEVER GUESS A FULL NAME.
- Loop Breaking: If the user provides a more specific name (e.g. 'Arjun Patel') in the current message or history to resolve an earlier ambiguity, you can then proceed with the SCHEDULE/CANCEL intent for that specific person.
- Accuracy: Use exact names, roles, and departments from the system data. Never hallucinate names.
- Clean Text: DO NOT use any emojis, icons, logos, or special ASCII art (like 📅, ✅, ❌, or 👤). Use only plain, professional text.
- Q&A: When asked about roles or departments, list them clearly from the provided system data.
- Tone: Be professional, helpful, and concise.
- Memory: Look back at the chat history! If the user already gave you the 'Time' in a previous message, use that time for the current scheduling request.

Return ONLY a JSON object:
{{
  "intent": "SCHEDULE" | "CANCEL" | "QUERY",
  "readiness": "READY" | "MISSING_INFO",
  "data": {{
    "candidate_name": "Full Name",
    "datetime": "Readable Datetime"
  }},
  "reply": "Your conversational response here"
}}

User Message: "{user_text}"
"""
    groq_messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages, # Send the whole memory here!
            response_format={"type": "json_object"}
        )

        raw_text = response.choices[0].message.content.strip()
        return json.loads(raw_text)

    except Exception as e:
        print("LLM Error:", e)
        return None