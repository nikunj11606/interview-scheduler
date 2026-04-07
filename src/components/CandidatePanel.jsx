import { useState } from 'react'
import './Panel.css'

function CandidatePanel({ candidates }) {
    const [selectedId, setSelectedId] = useState(null)
    const [searchTerm, setSearchTerm] = useState('') // New state for search

    function handleClick(id) {
        setSelectedId(selectedId === id ? null : id)
    }

    // Filter logic: Checks if name or role includes the search string
    const filteredCandidates = candidates.filter(candidate =>
        candidate.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        candidate.role.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <div className="panel">
            <div className="panel-header">
                <div className="header-left">
                    <span className="panel-header-title">Candidates</span>
                </div>
                <span className="panel-header-count">{filteredCandidates.length}</span>
            </div>

            {/* --- NEW SEARCH BAR --- */}
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
                        placeholder="Search by name or role..."
                        className="search-input"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            <div className="panel-list">
                {filteredCandidates.length > 0 ? (
                    filteredCandidates.map((candidate, index) => (
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
                                <span className={`status-pill ${candidate.status}`}>
                                    {candidate.status.toUpperCase()}
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
                                            <div className="detail-row">
                                                <span className="detail-label">Email</span>
                                                <span className="detail-value">{candidate.email}</span>
                                            </div>
                                        </>
                                    ) : (
                                        <p className="no-data-text">No interview scheduled yet</p>
                                    )}
                                </div>
                            )}
                        </div>
                    ))
                ) : (
                    <div className="empty-state">No candidates found</div>
                )}
            </div>
        </div>
    )
}

export default CandidatePanel