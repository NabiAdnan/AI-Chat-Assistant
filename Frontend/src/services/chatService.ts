import type { ChatRequest, Conversation } from "../types/chat";

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8001").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}/api${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...init?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`Request failed (${response.status}): ${await response.text()}`);
  }
  return response.json() as Promise<T>;
}

export function getConversations(): Promise<Conversation[]> {
  return request<Conversation[]>("/conversations");
}

export function getConversation(id: string): Promise<Conversation> {
  return request<Conversation>(`/conversations/${encodeURIComponent(id)}`);
}

export async function deleteConversation(id: string): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api/conversations/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`Unable to delete conversation (${response.status}): ${await response.text()}`);
  }
}

export async function renameConversation(id: string, title: string): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api/conversations/${encodeURIComponent(id)}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ title }),
  });
  if (!response.ok) {
    throw new Error(`Unable to rename conversation (${response.status}): ${await response.text()}`);
  }
}

function extractText(payload: string): string {
  if (payload === "[DONE]") return "";
  try {
    const data: unknown = JSON.parse(payload);
    if (typeof data === "string") return data;
    if (data && typeof data === "object") {
      const record = data as Record<string, unknown>;
      const choices = record.choices;
      if (Array.isArray(choices) && choices[0] && typeof choices[0] === "object") {
        const choice = choices[0] as Record<string, unknown>;
        const delta = choice.delta;
        if (delta && typeof delta === "object" && typeof (delta as Record<string, unknown>).content === "string") {
          return (delta as Record<string, string>).content;
        }
      }
      for (const key of ["delta", "content", "text", "token"]) {
        if (typeof record[key] === "string") return record[key] as string;
      }
    }
    return "";
  } catch {
    return payload;
  }
}

export async function streamChat(
  input: ChatRequest,
  onChunk: (chunk: string) => void,
  signal: AbortSignal,
  endpoint = "/chat",
): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api${endpoint}`, {
    method: "POST",
    signal,
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream, text/plain, application/json",
    },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    throw new Error(`Chat request failed (${response.status}): ${await response.text()}`);
  }
  if (!response.body) throw new Error("The server did not provide a readable response stream.");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  const isEventStream = response.headers.get("content-type")?.includes("text/event-stream") ?? false;
  let buffer = "";

  const emitEvent = (event: string) => {
    const data = event
      .split(/\r?\n/)
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).replace(/^ /, ""))
      .join("\n");
    if (data && data !== "[DONE]") onChunk(extractText(data));
  };

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (isEventStream) {
        buffer += decoder.decode(value, { stream: !done });
        const events = buffer.split(/\r?\n\r?\n/);
        buffer = events.pop() ?? "";
        events.forEach(emitEvent);
      } else if (value) {
        onChunk(decoder.decode(value, { stream: !done }));
      } else if (done) {
        const remaining = decoder.decode();
        if (remaining) onChunk(remaining);
      }
      if (done) break;
    }
    if (isEventStream && buffer.trim()) emitEvent(buffer);
  } finally {
    reader.releaseLock();
  }
}
