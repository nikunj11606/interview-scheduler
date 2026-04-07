import json
import os

DATA_FILE = "data.json"

def normalize(name: str) -> str:
    return name.strip().lower()

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: data.json not found")
        return {"candidates": [], "interviewers": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_candidate_email(name: str) -> str:
    data = load_data()
    for candidate in data["candidates"]:
        if normalize(candidate["name"]) == normalize(name):
            return candidate["email"]
    return None

def get_interviewer_email(name: str) -> str:
    data = load_data()
    for interviewer in data["interviewers"]:
        if normalize(interviewer["name"]) == normalize(name):
            return interviewer["email"]
    return None

def get_available_interviewers():
    data = load_data()
    return [iv["name"] for iv in data["interviewers"] if iv["available"]]

def update_interviewer_availability(name: str, candidate_name: str) -> bool:
    data = load_data()
    for iv in data["interviewers"]:
        if normalize(iv["name"]) == normalize(name):
            iv["available"] = False
            iv["candidate"] = candidate_name
            save_data(data)
            return True
    return False

def get_all_candidates():
    return load_data()["candidates"]

def get_all_interviewers():
    return load_data()["interviewers"]