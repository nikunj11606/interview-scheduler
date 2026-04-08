import { useState } from 'react'
import './Panel.css'

function InterviewerPanel({ interviewers }) {
    const [selectedId, setSelectedId] = useState(null)
    const [searchTerm, setSearchTerm] = useState('')

    function handleClick(id) {
        setSelectedId(selectedId === id ? null : id)
    }

    // Filter logic for Interviewers
    const filteredInterviewers = interviewers.filter(interviewer =>
        interviewer.name.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <div className="panel interviewers-panel">
            <div className="panel-header">
                <span className="panel-header-title">Interviewers</span>
                <span className="panel-header-count">{filteredInterviewers.length}</span>
            </div>

            {/* Added Search Bar */}
            <div className="search-container">
                <div className="search-wrapper">
                    <svg
                        className="search-icon"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                    >
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <input
                        type="text"
                        placeholder="Search by name..."
                        className="search-input"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            <div className="panel-list">
                {filteredInterviewers.length > 0 ? (
                    filteredInterviewers.map((interviewer, index) => (
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
                                    <div className="person-role">{interviewer.department}</div>
                                </div>
                                {/* Updated from status-dot to status-pill */}
                                <span className={`status-pill ${interviewer.available ? 'available' : 'scheduled'}`}>
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
                                            <div className="detail-row">
                                                <span className="detail-label">Email</span>
                                                <span className="detail-value">{interviewer.email}</span>
                                            </div>
                                        </>
                                    ) : (
                                        <>
                                            <div className="detail-row">
                                                <span className="detail-label">Email</span>
                                                <span className="detail-value">{interviewer.email}</span>
                                            </div>
                                            <p className="no-data-text" style={{ marginBottom: '8px' }}>No interviews assigned</p>
                                        </>
                                    )}
                                </div>
                            )}
                        </div>
                    ))
                ) : (
                    <div className="empty-state">No interviewers found</div>
                )}
            </div>
        </div>
    )
}

export default InterviewerPanel