import { useState } from 'react'
import './Panel.css'

function InterviewerPanel({ interviewers }) {
    const [selectedId, setSelectedId] = useState(null)

    function handleClick(id) {
        setSelectedId(selectedId === id ? null : id)
    }

    return (
        <div className="panel interviewers-panel">
            <div className="panel-header">
                <span className="panel-header-title">Interviewers</span>
                <span className="panel-header-count">{interviewers.length}</span>
            </div>
            <div className="panel-list">
                {interviewers.map((interviewer, index) => (
                    <div
                        key={interviewer.id}
                        className={`person-card
              ${selectedId === interviewer.id ? 'active' : ''}
              ${!interviewer.available ? 'scheduled-card' : ''}
            `}
                        style={{ animationDelay: `${index * 60}ms` }}
                        onClick={() => handleClick(interviewer.id)}
                    >
                        <div className="card-top">
                            <div>
                                <div className="person-name">{interviewer.name}</div>
                            </div>
                            <span className={`status-dot ${interviewer.available ? 'available' : 'busy'}`}>
                                {interviewer.available ? 'available' : 'scheduled'}
                            </span>
                        </div>

                        {selectedId === interviewer.id && (
                            <div className="detail-box">
                                {!interviewer.available ? (
                                    <>
                                        <div className="detail-row">
                                            <span className="detail-label">Candidate</span>
                                            <span className="detail-value">{interviewer.candidate}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="detail-label">At</span>
                                            <span className="detail-value">{interviewer.time}</span>
                                        </div>
                                    </>
                                ) : (
                                    <p className="no-data">no interviews assigned</p>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}

export default InterviewerPanel