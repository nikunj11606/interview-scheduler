import { useState, useEffect } from 'react'
import CandidatePanel from './components/CandidatePanel'
import InterviewerPanel from './components/InterviewerPanel'
import ChatWindow from './components/ChatWindow'
import './App.css'

function App() {
  const [candidateList, setCandidateList] = useState([])
  const [interviewerList, setInterviewerList] = useState([])

  // Fetch real data from the backend on app load
  useEffect(() => {
    fetch('http://127.0.0.1:8000/data')
      .then(res => res.json())
      .then(data => {
        setCandidateList(data.candidates);
        setInterviewerList(data.interviewers);
      });
  }, []);

  const scheduledCount = candidateList.filter(c => c.status === 'scheduled').length
  const availableCount = interviewerList.filter(i => i.available).length

  return (
    <div className="app-wrapper">
      <div className="gradient-line" />

      <div className="topbar">
        <div className="topbar-left">
          <div className="topbar-logo">
            <svg viewBox="0 0 24 24" fill="none" strokeWidth="2"
              strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
          </div>
          <span className="topbar-title">Interview Scheduler</span>
        </div>

        <div className="topbar-right">
          <div className='topbar-subtitle'>Interviewers</div>
          <div className="stat-item">
            <span className="stat-value">{scheduledCount}</span>
            <span className="stat-label">Scheduled</span>
          </div>
          <div className="stat-divider" />
          <div className="stat-item">
            <span className="stat-value">{availableCount}</span>
            <span className="stat-label">Available</span>
          </div>
        </div>
      </div>

      <div className="panels">
        <CandidatePanel candidates={candidateList} />
        <ChatWindow
          setCandidates={setCandidateList}
          setInterviewers={setInterviewerList}
        />
        <InterviewerPanel interviewers={interviewerList} />
      </div>
    </div>
  )
}

export default App