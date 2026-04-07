from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from llm import extract_details
from json_reader import (
    get_candidate_email,
    get_interviewer_email,
    get_available_interviewers,
    update_interviewer_availability,
    get_all_candidates,
    get_all_interviewers,
    load_data,
    save_data,
    normalize
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

    # Step 1 — extract candidate name and datetime from LLM
    extracted = extract_details(user_text)

    if not extracted:
        return {
            "reply": "I could not understand that request. Please try again.",
            "scheduled": False,
            "data": None
        }

    candidate_name = extracted.get("candidate_name")
    datetime_value = extracted.get("datetime")

    if not candidate_name or not datetime_value:
        return {
            "reply": "Please mention the candidate name and interview time.",
            "scheduled": False,
            "data": None
        }

    # Step 2 — load fresh data from JSON file
    data = load_data()
    candidates = data["candidates"]
    interviewers = data["interviewers"]

    # Step 3 — find candidate using normalize for case insensitive match
    candidate = next(
        (c for c in candidates if normalize(c["name"]) == normalize(candidate_name)),
        None
    )

    if not candidate:
        return {
            "reply": f"Candidate '{candidate_name}' was not found in the system.",
            "scheduled": False,
            "data": None
        }

    # Step 4 — find available interviewer
    interviewer = next(
        (i for i in interviewers if i["available"]),
        None
    )

    if not interviewer:
        return {
            "reply": "No interviewers are available right now.",
            "scheduled": False,
            "data": None
        }

    # Step 5 — update candidate status
    candidate["status"] = "scheduled"
    candidate["interviewTime"] = datetime_value
    candidate["interviewer"] = interviewer["name"]

    # Step 6 — update interviewer status
    interviewer["available"] = False
    interviewer["candidate"] = candidate_name
    interviewer["time"] = datetime_value

    # Step 7 — save updated data back to JSON file
    save_data(data)

    # Step 8 — send confirmation emails
    candidate_email = candidate["email"]
    interviewer_email = interviewer["email"]

    email_sent = send_confirmation(
        candidate_name=candidate["name"],
        candidate_email=candidate_email,
        interviewer_name=interviewer["name"],
        interviewer_email=interviewer_email,
        interview_datetime=datetime_value
    )

    # Step 9 — return response to React
    return {
    "reply": f"Interview scheduled for {candidate['name']}...",
    "scheduled": True,
    "data": {
        "candidate": candidate,
        "interviewer": interviewer,
        "candidate_email": candidate_email,
        "interviewer_email": interviewer_email
    }
}