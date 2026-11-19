# Nexus AI

A responsive React + Vite chat interface prepared for a FastAPI streaming backend.

## Run locally

```sh
npm install
cp .env.example .env.local
npm run dev
```

The app starts in a clearly labeled local demo mode (`VITE_DEMO_MODE=true`) with sample conversations and immediate, non-streamed sample replies. Set `VITE_DEMO_MODE=false` to use the API client, and set `VITE_API_BASE_URL` to the FastAPI origin. No API credentials belong in this frontend.

## Backend contract

The API client calls:

- `GET /api/conversations` → `Conversation[]`
- `GET /api/conversations/{id}` → `Conversation`
- `DELETE /api/conversations/{id}`
- `POST /api/chat` for new messages
- `POST /api/chat/regenerate` to replace an assistant response

Chat and regenerate requests send `{ "conversation_id": "...", "message": "...", "tone": "Professional" }`. Chat responses are read from a `text/event-stream` or plain-text response body. For SSE, each event should contain a `data:` field with either text or JSON containing a `delta`, `content`, `text`, or `token` string; `[DONE]` ends the stream. The stream is cancelled when the user stops generation or switches conversations.

Conversation titles can be renamed in the interface. Persisting a rename requires a backend endpoint, which is not part of the API contract above.
