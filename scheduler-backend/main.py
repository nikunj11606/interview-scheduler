from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
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
            "is_error": False,
            "email_sent": False,
            "action_type": "QUERY"
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

        # Send Cancellation Email
        email_success = False
        if interviewer:
            email_success = send_confirmation(
                candidate_name=candidate["name"],
                candidate_email=candidate["email"],
                interviewer_name=interviewer["name"],
                interviewer_email=interviewer["email"],
                interview_datetime=candidate.get("interviewTime", "TBD"),
                action="CANCELED"
            )

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
        return {
            "reply": ai_reply, 
            "scheduled": False, 
            "data": None, 
            "is_error": False, 
            "email_sent": email_success,
            "action_type": "CANCELED"
        }

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

        # VALIDATION: Parse Datetime
        try:
            parsed_time = datetime.strptime(datetime_value, "%B %d, %Y at %I:%M %p")
            now = datetime.now()
            
            # 1. Past Date Check
            if parsed_time < now:
                return {
                    "reply": f"I can't schedule an interview in the past ({datetime_value}). Please provide a future date and time.",
                    "scheduled": False, "data": None, "is_error": True
                }
            
        except ValueError:
            # If parsing fails, it's likely a weird format from LLM
            return {
                "reply": f"The date format provided ('{datetime_value}') is invalid. Please try again with something like 'April 10, 2026 at 10:00 AM'.",
                "scheduled": False, "data": None, "is_error": True
            }

        interviewer_name_val = action_data.get("interviewer_name")
        is_specified = action_data.get("is_interviewer_specified", False)

        interviewer = None

        if is_specified and interviewer_name_val:
            # SEARCH: Look for requested interviewer
            interviewer = next((i for i in interviewers if normalize(interviewer_name_val) in normalize(i["name"])), None)
            
            if not interviewer:
                return {"reply": f"I couldn't find an interviewer named '{interviewer_name_val}'.", "scheduled": False, "data": None, "is_error": True}
            
            if not interviewer["available"]:
                return {"reply": f"{interviewer['name']} is currently not available. Please pick another interviewer or let me suggest one.", "scheduled": False, "data": None, "is_error": True}
        
        elif interviewer_name_val:
            # USE AI SUGGESTION (Smart Match)
            suggested_interviewer = next((i for i in interviewers if normalize(i["name"]) == normalize(interviewer_name_val)), None)
            
            if suggested_interviewer and suggested_interviewer["available"]:
                # TIER 1: Use the AI's exact suggestion
                interviewer = suggested_interviewer
            else:
                # TIER 2: Try to find another interviewer in the same department
                dept = suggested_interviewer["department"] if suggested_interviewer else None
                if dept:
                    interviewer = next((i for i in interviewers if i["available"] and i["department"] == dept), None)
                
                # TIER 3: Global fallback (if Tier 1 and Tier 2 both fail)
                if not interviewer:
                    interviewer = next((i for i in interviewers if i["available"]), None)
        
        else:
            # FULL FALLBACK: Just pick anyone available
            interviewer = next((i for i in interviewers if i["available"]), None)

        if not interviewer:
            return {"reply": "No interviewers are available at this time.", "scheduled": False, "data": None, "is_error": True}

        # SILENT SYNC: If AI's suggested interviewer was busy, update the reply silently to match the final choice
        if interviewer_name_val and normalize(interviewer["name"]) != normalize(interviewer_name_val):
            ai_reply = ai_reply.replace(interviewer_name_val, interviewer["name"])

        # Update and Save
        candidate["status"] = "scheduled"
        candidate["interviewTime"] = datetime_value
        candidate["interviewer"] = interviewer["name"]
        interviewer["available"] = False
        interviewer["candidate"] = candidate_name
        interviewer["time"] = datetime_value
        
        save_data(data)

        email_success = send_confirmation(
            candidate_name=candidate["name"],
            candidate_email=candidate["email"],
            interviewer_name=interviewer["name"],
            interviewer_email=interviewer["email"],
            interview_datetime=datetime_value,
            action="SCHEDULED"
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
            "is_error": False,
            "email_sent": email_success,
            "action_type": "SCHEDULED"
        }

    # CASE D: User wants to RESCHEDULE an interview
    elif intent == "RESCHEDULE":
        candidate_name = action_data.get("candidate_name")
        datetime_value = action_data.get("datetime")
        interviewer_name_val = action_data.get("interviewer_name")

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

        if candidate.get("status") != "scheduled":
            return {"reply": f"{candidate['name']} doesn't have an interview scheduled right now.", "scheduled": False, "data": None, "is_error": True}

        old_time = candidate.get("interviewTime")
        old_interviewer_name = candidate.get("interviewer")
        
        # 1. Resolve Time
        new_time = datetime_value if datetime_value else old_time
        if datetime_value:
            try:
                parsed_time = datetime.strptime(datetime_value, "%B %d, %Y at %I:%M %p")
                if parsed_time < datetime.now():
                    return {"reply": f"I can't reschedule to a past date ({datetime_value}).", "scheduled": False, "data": None, "is_error": True}
            except ValueError:
                pass # Rely on LLM formatting

        # 2. Resolve Interviewer
        new_interviewer = None
        if interviewer_name_val:
            new_interviewer = next((i for i in interviewers if normalize(interviewer_name_val) in normalize(i["name"]) and i["available"]), None)
            if not new_interviewer:
                return {"reply": f"Interviewer '{interviewer_name_val}' is not available or not found.", "scheduled": False, "data": None, "is_error": True}
        else:
            new_interviewer = next((i for i in interviewers if normalize(old_interviewer_name) == normalize(i["name"])), None)

        # 3. Perform Updates
        # Free old interviewer if changing interviewers
        if interviewer_name_val and new_interviewer and new_interviewer["name"] != old_interviewer_name:
            old_i = next((i for i in interviewers if normalize(old_interviewer_name) == normalize(i["name"])), None)
            if old_i:
                old_i["available"] = True
                old_i.pop("candidate", None)
                old_i.pop("time", None)

        # Lock in new data
        candidate["interviewTime"] = new_time
        candidate["interviewer"] = new_interviewer["name"]
        
        new_interviewer["available"] = False
        new_interviewer["candidate"] = candidate_name
        new_interviewer["time"] = new_time
        
        save_data(data)

        email_success = send_confirmation(
            candidate_name=candidate["name"],
            candidate_email=candidate["email"],
            interviewer_name=new_interviewer["name"],
            interviewer_email=new_interviewer["email"],
            interview_datetime=new_time,
            action="RESCHEDULED"
        )

        return {
            "reply": ai_reply,
            "scheduled": True,
            "data": {
                "candidate": candidate,
                "interviewer": new_interviewer,
                "candidate_email": candidate["email"],
                "interviewer_email": new_interviewer["email"]
            },
            "is_error": False,
            "email_sent": email_success,
            "action_type": "RESCHEDULED"
        }

    return {"reply": ai_reply, "scheduled": False, "data": None}