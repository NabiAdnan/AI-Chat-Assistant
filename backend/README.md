# Nexus AI – FastAPI Backend (Google Gemini & OpenAI Supported)

A production-ready asynchronous backend for **Nexus AI**, built with **Python 3.12+**, **FastAPI**, **MongoDB**, and the official **Google GenAI SDK** (with optional OpenAI fallback).

## Key Architecture & Features

- **Primary AI Provider: Google Gemini**:
  - Uses the official `google-genai` SDK (`gemini-2.5-flash` by default).
  - High speed, free tier support via [Google AI Studio](https://aistudio.google.com).
- **Asynchronous & Non-blocking**: Uses `motor` (asynchronous MongoDB driver) and `client.aio.models.generate_content_stream` for high-concurrency streaming.
- **Server-Sent Events (SSE)**: True streaming responses without buffering, matching the frontend's streaming event parser.
- **Tone Personalities**:
  - `Professional`: Structured explanations, formal language, technical precision.
  - `Casual`: Approachable, friendly, conversational tone.
  - `Concise`: Direct, brief, high-density essential information.
- **MongoDB Persistence**:
  - Embedded message schema within conversations.
  - Automatic indexing on `updated_at` (descending).
  - Resilient ObjectId & client-side ID query abstraction.
- **Conversation Management**:
  - List conversations with pagination (`limit`, `skip`).
  - Retrieve full message histories.
  - In-place response regeneration without duplicating user prompts.
  - Title renaming and conversation deletion.
- **Graceful Error Handling & Security**:
  - Pydantic v2 input validation with whitespace rejection.
  - Sanitized error states that don't expose stack traces or secret keys.
  - Safe partial message persistence on client disconnections.

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app entry point, lifespan & CORS
│   ├── core/
│   │   ├── config.py            # Pydantic BaseSettings (.env loading)
│   │   └── prompts.py           # Tone definitions & system prompt builder
│   ├── database/
│   │   └── mongodb.py           # Async Motor connection & indexing
│   ├── models/
│   │   ├── conversation.py      # MongoDB conversation document model
│   │   └── message.py           # Embedded message model
│   ├── schemas/
│   │   ├── chat.py              # ChatRequest, RegenerateRequest schemas
│   │   └── conversation.py      # Conversation list, response & rename schemas
│   ├── routes/
│   │   ├── chat.py              # /api/chat & /api/chat/regenerate routes
│   │   └── conversations.py     # /api/conversations CRUD routes
│   ├── services/
│   │   ├── ai_service.py        # Google GenAI & OpenAI async streaming & error handling
│   │   ├── chat_service.py      # Context assembly, streaming & DB saving
│   │   └── conversation_service.py # MongoDB CRUD logic
│   └── utils/
│       ├── helpers.py           # ID query builder & schema serializers
│       └── streaming.py         # SSE data frame formatters
├── tests/
│   ├── test_chat.py             # Chat streaming, tones, regeneration tests
│   └── test_conversations.py    # Conversation CRUD and pagination tests
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Quickstart

### 1. Prerequisites

- Python 3.12+
- MongoDB running locally on `localhost:27017`
- A Google Gemini API Key (get one free at [Google AI Studio](https://aistudio.google.com/app/apikey))
- Node.js & npm (for the React frontend)

### 2. Environment Configuration

In `backend/.env`:

```env
# AI Provider: gemini (default) or openai
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Optional OpenAI fallback:
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# MongoDB Configuration:
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=nexus_ai

# Frontend Integration:
FRONTEND_URL=http://localhost:5173
```

### 3. Install Dependencies

```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Run the Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

- Swagger Interactive Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 5. Run the Automated Tests

```bash
pytest tests -v
```

---

## API Reference

### Chat & Streaming

#### `POST /api/chat`
Stream AI response tokens for a user prompt using Gemini.
- **Request Body**:
  ```json
  {
    "conversation_id": "optional-id",
    "message": "Explain how transformers work in AI.",
    "tone": "Professional"
  }
  ```
- **Response**: `text/event-stream`
  - Chunk: `data: {"content": "..."}\n\n`
  - Completion: `data: {"status": "completed", "conversation_id": "..."}\n\n`
  - Termination: `data: [DONE]\n\n`

#### `POST /api/chat/regenerate`
Regenerate the latest assistant reply for a conversation.
- **Request Body**:
  ```json
  {
    "conversation_id": "673cf0f7...",
    "tone": "Casual"
  }
  ```
- **Response**: `text/event-stream`

---

### Conversations Management

#### `GET /api/conversations`
Retrieve all conversations sorted by latest activity.
- Query parameters: `limit` (default: 50), `skip` (default: 0)

#### `GET /api/conversations/{id}`
Retrieve a single conversation including all messages.

#### `PATCH /api/conversations/{id}`
Rename a conversation title (`{ "title": "New Title" }`).

#### `DELETE /api/conversations/{id}`
Permanently delete a conversation.
