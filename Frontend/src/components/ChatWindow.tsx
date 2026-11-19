import { useEffect, useRef } from "react";
import type { ChatMessage as ChatMessageType, Feedback } from "../types/chat";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";
import WelcomeScreen from "./WelcomeScreen";

interface ChatWindowProps {
  messages: ChatMessageType[];
  isGenerating: boolean;
  onSend: (message: string) => void;
  onStop: () => void;
  onRegenerate: (id: string) => void;
  onFeedback: (id: string, feedback: Feedback) => void;
}

export default function ChatWindow({ messages, isGenerating, onSend, onStop, onRegenerate, onFeedback }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: isGenerating ? "smooth" : "auto", block: "end" });
  }, [messages, isGenerating]);

  return (
    <main className="flex min-h-0 flex-1 flex-col">
      <div className="chat-scroll min-h-0 flex-1">
        {messages.length === 0 ? (
          <WelcomeScreen onSuggestion={onSend} />
        ) : (
          <div className="mx-auto flex w-full max-w-[820px] flex-col gap-7 px-5 pb-8 pt-8 sm:px-7 sm:pt-10">
            {messages.map((message, index) => (
              <ChatMessage
                key={message.id}
                message={message}
                isGenerating={isGenerating && message.role === "assistant" && index === messages.length - 1}
                onRegenerate={() => onRegenerate(message.id)}
                onFeedback={(feedback) => onFeedback(message.id, feedback)}
                disableActions={isGenerating}
              />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
      <ChatInput onSend={onSend} onStop={onStop} isGenerating={isGenerating} />
    </main>
  );
}
