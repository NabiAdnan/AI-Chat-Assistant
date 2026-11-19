import { ArrowUp, Square } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop: () => void;
  isGenerating: boolean;
  disabled?: boolean;
}

export default function ChatInput({ onSend, onStop, isGenerating, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`;
  }, [value]);

  function submit() {
    const message = value.trim();
    if (!message || isGenerating || disabled) return;
    onSend(message);
    setValue("");
  }

  return (
    <div className="chat-input-area px-4 pb-4 pt-3 sm:px-7 sm:pb-5">
      <div className="mx-auto max-w-[820px]">
        <div className="input-shell">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                submit();
              }
            }}
            placeholder="Message Nexus AI..."
            aria-label="Message Nexus AI"
            rows={1}
            disabled={isGenerating}
          />
          {isGenerating ? (
            <button type="button" className="send-button stop-button" onClick={onStop} aria-label="Stop generating" title="Stop generating">
              <Square size={14} fill="currentColor" />
            </button>
          ) : (
            <button
              type="button"
              className={`send-button ${value.trim() ? "send-button-active" : ""}`}
              onClick={submit}
              disabled={!value.trim() || disabled}
              aria-label="Send message"
              title="Send message"
            >
              <ArrowUp size={18} strokeWidth={2.2} />
            </button>
          )}
        </div>
        <p className="mt-2.5 text-center text-[10px] text-slate-400 dark:text-slate-500">
          AI can make mistakes. Verify important information.
          <span className="hidden sm:inline"> · Enter to send, Shift + Enter for a new line</span>
        </p>
      </div>
    </div>
  );
}
