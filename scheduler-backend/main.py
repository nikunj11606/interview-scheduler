from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from llm_groq import process_request
from json_reader import (
    load_data,
    save_data,
    normalize,
    get_all_candidates,
    get_all_interviewers
)
from email_sender import send_confirmation

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = [] # New field to accept chat history

@app.get("/")
def root():
    return {"status": "Interview Scheduler API is running"}

@app.get("/data")
def get_data():
    return {
        "candidates": get_all_candidates(),
        "interviewers": get_all_interviewers()
    }

@app.post("/chat")
def chat(request: ChatRequest):
    user_text = request.message
    history = request.history # Capture the history

    # Step 1 — Load data to provide context to LLM
    data = load_data()
    candidates = data["candidates"]
    interviewers = data["interviewers"]

    # Step 2 — Create data summary for context-aware Q&A
    summary = "Current Candidates:\n"
    for c in candidates:
        interviewer = c.get('interviewer', 'None')
        summary += f"- {c['name']} (Role: {c['role']}, Status: {c['status']}, Time: {c.get('interviewTime', 'None')}, Interviewer: {interviewer})\n"
    
    summary += "\nInterviewers:\n"
    for i in interviewers:
        assigned = f", Assigned to: {i.get('candidate')} at {i.get('time')}" if not i['available'] else ""
        summary += f"- {i['name']} (Department: {i['department']}, Available: {i['available']}{assigned})\n"

    # Step 3 — Process request via Groq (now passing history)
    result = process_request(user_text, summary, history)

    if not result:
        return {"reply": "Error connecting to AI.", "scheduled": False, "data": None, "is_error": True}

    intent = result.get("intent")
    readiness = result.get("readiness", "READY")
    ai_reply = result.get("reply", "Done.")
    action_data = result.get("data", {})

    # MIDDLE GROUND: If LLM knows it is missing required information, stop and reply normally
    if readiness == "MISSING_INFO":
        return {
            "reply": ai_reply,
            "scheduled": False,
            "data": None,
            "is_error": False
        }

    # CASE A: User is just asking a question or chatting
    if intent == "QUERY":
        return {
            "reply": ai_reply,
            "scheduled": False,
            "data": None,
            "is_error": False # This stops the ❌ from showing up
        }

    # CASE B: User wants to CANCEL an interview
    if intent == "CANCEL":
        candidate_name = action_data.get("candidate_name")
        
        # SEARCH LOGIC: Look for all potential matches
        matches = [c for c in candidates if normalize(candidate_name) in normalize(c["name"])]
        exact_match = next((c for c in matches if normalize(c["name"]) == normalize(candidate_name)), None)

        if exact_match:
            candidate = exact_match
        elif len(matches) > 1:
            names = ", ".join([c["name"] for c in matches])
            return {"reply": f"I found multiple matches: {names}. Which one did you mean?", "scheduled": False, "data": None, "is_error": True}
        else:
            candidate = matches[0] if len(matches) == 1 else None
        
        if not candidate:
            return {"reply": f"Sorry, I couldn't find a candidate named {candidate_name}.", "scheduled": False, "data": None, "is_error": True}

        if candidate["status"] != "scheduled":
            return {"reply": f"{candidate['name']} doesn't have an interview scheduled.", "scheduled": False, "data": None, "is_error": True}

        interviewer_name = candidate.get("interviewer")
        interviewer = None
        if interviewer_name:
            interviewer = next((i for i in interviewers if normalize(i["name"]) == normalize(interviewer_name)), None)

        # Reset Candidate
        candidate["status"] = "pending"
        candidate.pop("interviewTime", None)
        candidate.pop("interviewer", None)

        # Reset Interviewer
        if interviewer:
            interviewer["available"] = True
            interviewer.pop("candidate", None)
            interviewer.pop("time", None)

        save_data(data)
        return {"reply": ai_reply, "scheduled": False, "data": None, "is_error": False}

    # CASE C: User wants to SCHEDULE an interview
    if intent == "SCHEDULE":
        candidate_name = action_data.get("candidate_name")
        datetime_value = action_data.get("datetime")

        # SEARCH LOGIC: Look for all potential matches
        matches = [c for c in candidates if normalize(candidate_name) in normalize(c["name"])]
        exact_match = next((c for c in matches if normalize(c["name"]) == normalize(candidate_name)), None)

        if exact_match:
            candidate = exact_match
        elif len(matches) > 1:
            names = ", ".join([c["name"] for c in matches])
            return {"reply": f"I found multiple matches: {names}. Which one did you mean?", "scheduled": False, "data": None, "is_error": True}
        else:
            candidate = matches[0] if len(matches) == 1 else None
        
        if not candidate:
            return {"reply": f"Candidate '{candidate_name}' not found.", "scheduled": False, "data": None, "is_error": True}

        if candidate.get("status") == "scheduled":
            return {"reply": f"{candidate['name']} is already scheduled.", "scheduled": False, "data": None, "is_error": True}

        interviewer = next((i for i in interviewers if i["available"]), None)
        if not interviewer:
            return {"reply": "No interviewers available.", "scheduled": False, "data": None, "is_error": True}

        # Update and Save
        candidate["status"] = "scheduled"
        candidate["interviewTime"] = datetime_value
        candidate["interviewer"] = interviewer["name"]
        interviewer["available"] = False
        interviewer["candidate"] = candidate_name
        interviewer["time"] = datetime_value
        
        save_data(data)

        send_confirmation(
            candidate_name=candidate["name"],
            candidate_email=candidate["email"],
            interviewer_name=interviewer["name"],
            interviewer_email=interviewer["email"],
            interview_datetime=datetime_value
        )

        return {
            "reply": ai_reply,
            "scheduled": True,
            "data": {
                "candidate": candidate,
                "interviewer": interviewer,
                "candidate_email": candidate["email"],
                "interviewer_email": interviewer["email"]
            },
            "is_error": False
        }


    return {"reply": ai_reply, "scheduled": False, "data": None}