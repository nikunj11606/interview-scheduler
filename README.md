# AI Interview Scheduler

An AI-powered interview scheduling web application that enables users to schedule, reschedule, and cancel interviews through a natural language chat interface. The system automatically assigns interviewers, creates Google Calendar events with Google Meet links, and sends email notifications to both candidates and interviewers.

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** (Backend)
- **Node.js 18+** (Frontend)
- **React.js** (Frontend)
- **Google Cloud Account** (For Calendar API)
- **Groq/Gemini API Key**

### 2. Backend Setup
1. Navigate to the backend folder:
   ```bash
   cd scheduler-backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Prepare your `.env` file:
   ```env
   GROQ_API_KEY=your_key_here
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_app_password
   ALLOWED_ORIGINS=http://localhost:5173
   ```

### 3. Frontend Setup
1. From the root directory:
   ```bash
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```

---

## 📅 Google Calendar API Integration

To make the scheduling work, you need to create your own Google Cloud credentials.

### Step 1: Create a Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project named "Interview Scheduler".

### Step 2: Enable APIs
Enable the following APIs in the **Library** section:
- **Google Calendar API**
- **Google Meet API** (Required for the new "Open Access" meeting links)

### Step 3: OAuth Consent Screen
1. Go to **APIs & Services > OAuth consent screen**.
2. Select **External** and provide the app name and your email.
3. Add the following scopes:
   - `.../auth/calendar`
   - `.../auth/meetings.space.created`
4. Add your email address under **Test Users**.

### Step 4: Create Credentials
1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > OAuth client ID**.
3. Application type: **Desktop app**.
4. Download the JSON file and rename it to `oauth_client.json`.
5. Move this file into the `scheduler-backend/` folder.

### Step 5: Authenticate
Run the authentication script once to generate your `token.json`:
```bash
python authenticate_calendar.py
```
A browser window will open. Log in and hit **Allow**.

---

## 🛠 Features
- **AI-Powered Chat**: Natural language scheduling (e.g., "Schedule an interview for Nikunj tomorrow at 5pm").
- **Conflict Detection**: Checks both the system database and the interviewer's real-time Google Calendar availability.
- **Smart Meeting Links**: Generates Google Meet links with `OPEN` access (no host permission required).
- **Mobile Responsive**: Fully responsive UI and mobile-optimized HTML emails.
- **Automatic Transitions**: Interviewers are marked as busy/available automatically.

## 📁 Project Structure
- `/src`: React frontend (Vite).
- `/scheduler-backend`: FastAPI backend.
    - `main.py`: Primary API logic.
    - `calendar_service.py`: Google Calendar & Meet integration.
    - `email_sender.py`: Responsive email delivery.
    - `data.json`: Local storage for candidates and interviewers.

---

## ❓ Troubleshooting
- **Meeting Host Requirement**: If guests can't join without you, ensure you have enabled the **Google Meet API** and performed a fresh login with `authenticate_calendar.py`.
- **CORS Error**: Ensure `ALLOWED_ORIGINS` in your `.env` matches your frontend URL (usually `http://localhost:5173`).
- **Token Expired**: Simply delete `token.json` and run `python authenticate_calendar.py` again.
