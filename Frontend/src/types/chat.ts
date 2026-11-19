export type Tone = "Professional" | "Casual" | "Concise";
export type MessageRole = "user" | "assistant";
export type Feedback = "up" | "down";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
  feedback?: Feedback;
  error?: string;
}

export interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
  messages: ChatMessage[];
}

export interface ChatRequest {
  conversation_id: string;
  message: string;
  tone: Tone;
}
