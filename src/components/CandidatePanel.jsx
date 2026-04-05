import { useState } from 'react'
import './Panel.css'

function CandidatePanel({ candidates }) {
    const [selectedId, setSelectedId] = useState(null)

    function handleClick(id) {
        setSelectedId(selectedId === id ? null : id)
    }

    return (
        <div className="panel">
            <div className="panel-header">
                <span className="panel-header-title">Candidates</span>
                <span className="panel-header-count">{candidates.length}</span>
            </div>
            <div className="panel-list">
                {candidates.map((candidate, index) => (
                    <div
                        key={candidate.id}
                        className={`person-card
              ${selectedId === candidate.id ? 'active' : ''}
              ${candidate.status === 'scheduled' ? 'scheduled-card' : ''}
            `}
                        style={{ animationDelay: `${index * 60}ms` }}
                        onClick={() => handleClick(candidate.id)}
                    >
                        <div className="card-top">
                            <div>
                                <div className="person-name">{candidate.name}</div>
                                <div className="person-role">{candidate.role}</div>
                            </div>
                            <span className={`status-dot ${candidate.status}`}>
                                {candidate.status === 'scheduled' ? 'scheduled' : 'pending'}
                            </span>
                        </div>

                        {selectedId === candidate.id && (
                            <div className="detail-box">
                                {candidate.status === 'scheduled' ? (
                                    <>
                                        <div className="detail-row">
                                            <span className="detail-label">Time</span>
                                            <span className="detail-value">{candidate.interviewTime}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="detail-label">Interviewer</span>
                                            <span className="detail-value">{candidate.interviewer}</span>
                                        </div>
                                    </>
                                ) : (
                                    <p className="no-data">not scheduled yet</p>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}

export default CandidatePanel