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
You can handle four intents:
1. SCHEDULE: User wants to book a new interview.
2. CANCEL: User wants to cancel an existing interview.
3. RESCHEDULE: User already has an interview and wants to change the time, the interviewer, or both.
4. QUERY: User is asking a question, chatting, or making a request about the data.

Rules:
- If SCHEDULE: Extract 'candidate_name', 'datetime', and 'interviewer_name'.
- If RESCHEDULE: Extract 'candidate_name', and optionally 'datetime' or 'interviewer_name' if the user specifically requests changing them.
- Smart Matching: For SCHEDULE intents, if the user DOES NOT mention an interviewer, select the most suitable AVAILABLE interviewer from CURRENT SYSTEM DATA based on their role. (CRITICAL: NEVER auto-assign or change an interviewer for RESCHEDULE intents unless explicitly asked. Leave 'interviewer_name' null tracking the current person).
  - NO QUESTIONS: You MUST NOT ask the user for confirmation or choice of interviewers. Just pick the best one and proceed with the SCHEDULE intent immediately.
  - Mapping Guidance: 
    - Data Science / AI Research Depts: Data Analyst, Data Scientist, ML Engineer.
    - Design Dept: UI Designer.
    - Backend Dept: Backend Developer.
    - HR Dept: General soft-skill roles or if no technical match is found.
    - Engineering Dept: Frontend, Backend, App, System, Cloud, QA, DevOps Engineers.
- Specific Interviewer: If the user explicitly mentions an interviewer's name (e.g., "with Akash Singh"), set 'is_interviewer_specified' to true and extract that name.
- Strict Formatting: The 'datetime' MUST ALWAYS be in the format: Month DD, YYYY at HH:MM AM/PM (e.g., "April 10, 2026 at 2:30 PM").
- Relative Date Resolution: Automatically resolve terms like "tomorrow", "next Monday", or "day after tomorrow" into the absolute date based on Today's Date.
- Working Hours: Scheduling is ONLY allowed between 9:00 AM and 10:00 PM. If a user suggests a time outside this range, set "readiness" to "MISSING_INFO" and suggest a valid time.
- Mandatory Time: Users MUST specify a clear time (e.g., "tomorrow at 3 PM"). You are NO LONGER allowed to default to 10:00 AM. If the time is missing, set "readiness" to "MISSING_INFO" and ask the user for the time.
- If CANCEL: Identify 'candidate_name'.
- If QUERY: Don't add technical words like pending, None in reply. GIVE MORE HUMAN LIKE ANSWER based on CURRENT SYSTEM DATA.
- Readiness Rule: If SCHEDULE, you must have BOTH a valid 'candidate_name' AND a 'datetime'. If CANCEL, you must have a valid 'candidate_name'. If RESCHEDULE, you must have a valid 'candidate_name', AND at least one of 'datetime' or 'interviewer_name' to change. If ANY required information is missing from the chat history, you MUST set "readiness" to "MISSING_INFO", change intent to "QUERY", and ask the user for the missing details. Otherwise, set "readiness" to "READY".
- Ambiguity: If a user mentions a name that matches multiple candidates (e.g. 'Arjun'), do not schedule. Set "readiness" to "MISSING_INFO", intent to QUERY, and ask for clarification WITH THE LIST OF POSSIBLE NAMES. YOU MUST NEVER GUESS A FULL NAME.
- Loop Breaking: If the user provides a more specific name (e.g. 'Arjun Patel') in the current message or history to resolve an earlier ambiguity, you can then proceed with the SCHEDULE/CANCEL intent for that specific person.
- Accuracy: Use exact names, roles, and departments from the system data. Never hallucinate names.
- Clean Text: DO NOT use any emojis, icons, logos, or special ASCII art (like 📅, ✅, ❌, or 👤). Use only plain, professional text.
- Q&A: When asked about roles or departments, list them clearly from the provided system data.
- Up for Interview: Any candidate with status "pending" or "scheduled" is considered "up for an interview".
- Counting Breakdown: When asked "how many" candidates of a specific role are up for an interview (e.g., "How many Data Analysts..."):
  1. Use case-insensitive matching for the role.
  2. Provide the TOTAL count.
  3. Provide a breakdown: how many are scheduled (include names) and how many are pending (include names).
  4. Example: "There are 2 Data Analysts up for interviews: 1 scheduled (Drashti Rajgor) and 1 pending (Sai Pallavi)."

- Tone: Be professional, helpful, and concise.
- Memory: Look back at the chat history! If the user already gave you the 'Time' in a previous message, use that time for the current scheduling request.

Return ONLY a JSON object:
{{
  "intent": "SCHEDULE" | "CANCEL" | "RESCHEDULE" | "QUERY",
  "readiness": "READY" | "MISSING_INFO",
  "data": {{
    "candidate_name": "Full Name",
    "datetime": "Month DD, YYYY at HH:MM AM/PM",
    "interviewer_name": "Full Name",
    "is_interviewer_specified": true | false
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