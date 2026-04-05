export const candidates = [
    {
        id: 1,
        name: "Nikunj Sankaliya",
        role: "ML Engineer",
        status: "scheduled",
        interviewTime: "Tomorrow, 5:00 PM",
        interviewer: "Rahul Mehta"
    },
    {
        id: 2,
        name: "Priya Shah",
        role: "Frontend Developer",
        status: "scheduled",
        interviewTime: "Apr 6, 10:00 AM",
        interviewer: "Sneha Joshi"
    },
    {
        id: 3,
        name: "Arjun Verma",
        role: "Backend Developer",
        status: "pending",
        interviewTime: null,
        interviewer: null
    },
    {
        id: 4,
        name: "Kavya Nair",
        role: "UI Designer",
        status: "pending",
        interviewTime: null,
        interviewer: null
    }
]

export const interviewers = [
    {
        id: 1,
        name: "Rahul Mehta",
        available: false,
        candidate: "Nikunj Sankaliya",
        time: "Tomorrow, 5:00 PM"
    },
    {
        id: 2,
        name: "Sneha Joshi",
        available: false,
        candidate: "Priya Shah",
        time: "Apr 6, 10:00 AM"
    },
    {
        id: 3,
        name: "Amit Sharma",
        available: true,
        candidate: null,
        time: null
    }
]