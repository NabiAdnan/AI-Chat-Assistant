# 🚀 Nexus AI – Intelligent AI Chat Assistant

An intelligent, full-stack AI Chat Assistant built using **React, TypeScript, FastAPI, MongoDB, and OpenAI API**.

Developed as part of the **Quantiphi Vibe Coding Challenge – KITS Warangal**.

Nexus AI provides an interactive conversational experience with real-time AI response streaming, persistent conversation history, customizable response tones, and intelligent chat management.

---

## ✨ Features

### 1. AI-Powered Chat
- Integrated with OpenAI API for intelligent response generation.
- Supports contextual conversations.
- Maintains previous conversation history.
- Provides interactive user and AI message interfaces.

### 2. Real-Time Streaming
- Implements Server-Sent Events (SSE).
- Displays AI responses progressively as chunks arrive.
- Provides a real-time typing experience.
- Supports stopping ongoing response generation.

### 3. Conversation Management
- Create new conversations.
- View previous conversations.
- Switch between conversations.
- Search conversation history.
- Rename conversations.
- Delete conversations.
- Automatically persist conversations in MongoDB.

### 4. Dynamic Tone Selection

Users can customize AI responses using three different tones:

| Tone | Description |
|---|---|
| Professional | Formal, structured and informative responses |
| Casual | Friendly and conversational responses |
| Concise | Short and direct responses |

The selected tone is converted into a system instruction on the backend before sending the request to OpenAI.

### 5. Additional Features
- **Regenerate Response:** Generate a new response using the same conversation context.
- **Copy Response:** Copy AI-generated responses to the clipboard.
- Thumbs-up and thumbs-down feedback controls.
- Markdown rendering.
- Code block formatting and syntax highlighting.
- Light and dark themes.
- Responsive user interface.

---

## 🛠️ Technology Stack

### Frontend

- React.js
- TypeScript
- Vite
- Tailwind CSS
- Lucide React
- React Hooks
- Fetch API
- Server-Sent Events (SSE)

### Backend

- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic
- OpenAI Python SDK
- PyMongo Async

### Database

- MongoDB

### AI Integration

- OpenAI API

---

## 🏗️ System Architecture

```text
                  USER
                   |
                   v
          REACT FRONTEND
          (Vite + TypeScript)
                   |
                   | HTTP Requests / SSE
                   |
                   v
            FASTAPI BACKEND
                   |
          +--------+---------+
          |                  |
          v                  v
      OPENAI API          MONGODB
          |                  |
          v                  v
     AI RESPONSE       CONVERSATION
      GENERATION         STORAGE
          |
          v
    STREAMING RESPONSE
          |
          v
     REACT FRONTEND
          |
          v
    DISPLAY AI RESPONSE
```

### Application Workflow

1. The user enters a message in the React chat interface.
2. The frontend sends the message, conversation ID, and selected tone to FastAPI.
3. FastAPI validates the incoming request.
4. The backend retrieves the existing conversation context from MongoDB.
5. The selected tone is converted into a system instruction.
6. The backend sends the conversation context to OpenAI.
7. OpenAI generates a response using streaming.
8. FastAPI forwards response chunks to the frontend using SSE.
9. React progressively displays the generated response.
10. The completed AI response is saved in MongoDB.

---

## 📁 Project Structure

```text
Nexus-AI-Chat-Assistant/
│
├── Frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── .env.example
│   ├── package.json
│   └── README.md
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── prompts.py
│   │   │
│   │   ├── database/
│   │   │   └── mongodb.py
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── chat_service.py
│   │   │   └── conversation_service.py
│   │   │
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── tests/
│   │   ├── test_chat.py
│   │   └── test_conversations.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
│
├── .gitignore
└── README.md
```

---

## ⚙️ Installation and Setup

Follow these instructions to run Nexus AI locally.

### Prerequisites

Install the following:

- Python 3.12 or later
- Node.js and npm
- MongoDB Community Server
- OpenAI API key
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Nexus-AI-Chat-Assistant.git

cd Nexus-AI-Chat-Assistant
```

### 2. Configure MongoDB

Start your MongoDB server.

Default local connection:

```text
mongodb://localhost:27017
```

The application uses:

- Database: `nexus_ai`
- Collection: `conversations`

The backend creates the required database indexes during startup.

### 3. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file inside the `backend/` directory.

```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=nexus_ai

OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_supported_model

FRONTEND_URL=http://localhost:5173
```

Replace the OpenAI API key and model with your actual configuration.

**Important:** Never commit your `.env` file or expose your API key publicly.

### 5. Start the Backend Server

From the `backend` directory:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will run at:

```text
http://localhost:8000
```

FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

ReDoc documentation:

```text
http://localhost:8000/redoc
```

Health check:

```text
http://localhost:8000/api/health
```

---

## 🌐 Frontend Setup

Open a separate terminal.

Navigate to the frontend directory:

```bash
cd Frontend
```

Install dependencies:

```bash
npm install
```

Create or configure `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_DEMO_MODE=false
```

Start the development server:

```bash
npm run dev
```

Frontend will run at:

```text
http://localhost:5173
```

---

##  API Documentation

The backend exposes the following REST APIs:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check backend and database health |
| GET | `/api/conversations` | Retrieve all conversations |
| POST | `/api/conversations` | Create a conversation |
| GET | `/api/conversations/{id}` | Retrieve a conversation |
| PATCH | `/api/conversations/{id}` | Rename a conversation |
| DELETE | `/api/conversations/{id}` | Delete a conversation |
| POST | `/api/chat` | Send a message and receive a streamed response |
| POST | `/api/chat/regenerate` | Regenerate an AI response |

### Chat Request Example

```json
{
  "conversation_id": null,
  "message": "Explain machine learning",
  "tone": "Professional"
}
```

### Streaming Response

The chat endpoint uses Server-Sent Events.

Example event sequence:

```text
data: {"content": "Artificial"}

data: {"content": " intelligence"}

data: {"status": "completed", "conversation_id": "..."}

data: [DONE]
```

The frontend reads the stream and progressively updates the assistant message.

---

##  Database Design

MongoDB stores conversation data in the `conversations` collection.

Example document:

```json
{
  "_id": "MongoDB ObjectId",
  "title": "Python Interview Preparation",
  "messages": [
    {
      "role": "user",
      "content": "What is Python?",
      "timestamp": "2026-11-19T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Python is a high-level programming language.",
      "timestamp": "2026-11-19T10:00:05Z"
    }
  ],
  "created_at": "2026-11-19T10:00:00Z",
  "updated_at": "2026-11-19T10:00:05Z"
}
```

Messages are stored as embedded documents inside each conversation.

---

##  Testing

The backend includes automated tests for important application functionality.

Run tests from the backend directory:

```bash
pytest -v
```

Test coverage includes:

- Chat streaming.
- Tone validation.
- Empty message validation.
- Message persistence.
- Response regeneration.
- Streaming error handling.
- Health endpoint.
- Conversation creation and retrieval.
- Pagination.
- Conversation renaming.
- Conversation deletion.

---

##  Security Considerations

- API keys are stored in environment variables.
- OpenAI credentials remain on the backend.
- Incoming requests are validated using Pydantic.
- Conversation IDs are validated.
- CORS is configured for the frontend origin.
- API errors are handled without exposing internal stack traces.
- Environment files and sensitive configuration are excluded from Git.

---

## 🚀 Future Enhancements

Potential improvements include:

- User authentication and authorization.
- Multiple AI provider support (OpenAI and Claude).
- File uploads and document-based conversations.
- Retrieval-Augmented Generation (RAG).
- Conversation export functionality.
- Persistent user preferences.
- Advanced response feedback and analytics.
- Rate limiting and usage monitoring.

---

##  Project Information

**Project Name:** Nexus AI – Intelligent AI Chat Assistant

**Challenge:** Quantiphi Vibe Coding Challenge

**Institution:** Kakatiya Institute of Technology and Science (KITS), Warangal

**Category:** Full-Stack Development | Artificial Intelligence | Generative AI

---

## 📄 License

This project is developed for educational and demonstration purposes as part of the Quantiphi Vibe Coding Challenge.
