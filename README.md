# AI Sales Roleplay Agent

An AI-powered Business Development Representative (BDR) roleplay simulator that helps users practice professional sales conversations against realistic AI personas.

The application allows users to choose different customer personas, conversation scenarios, and difficulty levels before engaging in a natural conversation powered by Google's Gemini AI. At the end of each session, the application generates detailed feedback highlighting strengths, weaknesses, and suggestions for improvement.

---

## Live Demo

**Frontend**

https://sales-roleplay-agent.vercel.app

**Backend**

https://sales-roleplay-agent.onrender.com

---

## Features

- Multiple AI customer personas
- Multiple sales scenarios
- Three difficulty levels
- Multi-turn conversations
- Session management
- AI-generated customer responses
- Automatic conversation debrief
- Performance scoring
- Responsive React frontend
- REST API backend
- Cloud deployment

---

## Personas

- Startup Founder
- NGO Director
- HR Manager
- Procurement Manager
- Club President
- Potential Sponsor
- Small Business Owner

---

## Scenarios

- Discovery Call
- Pitch Delivery
- Objection Handling
- Need Diagnosis
- Follow-up Meeting

---

## Difficulty Levels

### Easy
- Friendly
- Helpful
- Gives detailed answers

### Medium
- Busy
- Realistic
- Needs convincing

### Hard
- Skeptical
- Challenges assumptions
- Difficult to convince

---

## Tech Stack

### Frontend

- React
- Vite
- Tailwind CSS
- Axios

### Backend

- Node.js
- Express.js

### AI

- Google Gemini API

### Deployment

- Vercel
- Render

### Version Control

- Git
- GitHub

---

## Project Structure

```
sales-roleplay-agent/

│
├── client/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── server/
│   ├── controllers/
│   ├── routes/
│   ├── services/
│   ├── prompts/
│   ├── data/
│   └── package.json
│
└── README.md
```

---

## Application Flow

```
User

↓

Select Persona

↓

Select Scenario

↓

Select Difficulty

↓

Session Created

↓

Chat with AI

↓

Conversation Stored

↓

End Session

↓

AI Debrief Generated

↓

Performance Report
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/Adarsh-0105/sales-roleplay-agent.git
```

Open the project

```bash
cd sales-roleplay-agent
```

### Backend

```bash
cd server
npm install
npm run dev
```

### Frontend

```bash
cd client
npm install
npm run dev
```

---

## Environment Variables

### Backend

Create a `.env` file inside the **server** folder.

```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
PORT=5000
```

### Frontend

Create a `.env.production` file inside **client**

```
VITE_API_URL=https://your-backend-url.onrender.com/api
```

---

## Sample Conversation

**You**

> Hi! Thanks for taking the time today. I'd like to understand how your team currently qualifies inbound leads.

**Startup Founder**

> We mostly use a mix of HubSpot and manual review. What's different about your solution?

**You**

> We automate the first stage of lead qualification so your SDRs spend time only on high-quality leads.

**Startup Founder**

> Interesting. How accurate is it?

---

## Future Improvements

- Voice conversations
- Speech-to-text
- Text-to-speech
- Authentication
- Conversation history database
- Advanced scoring analytics
- Industry-specific personas
- Dashboard for instructors
- Additional scenarios

---

## Author

**Kumar Adarsh**

BITS Pilani Goa Campus

B.E. Electronics and Communication Engineering

Practice School-I

Caarya Innovative Solutions Pvt. Ltd.

---

## License

This project was developed as part of the Practice School-I program at BITS Pilani.