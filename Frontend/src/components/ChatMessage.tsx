import { Bot, Check, Copy, UserRound } from "lucide-react";
import { useState, type ReactElement, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";
import type { ChatMessage as ChatMessageType, Feedback } from "../types/chat";
import MessageActions from "./MessageActions";

interface ChatMessageProps {
  message: ChatMessageType;
  isGenerating?: boolean;
  onRegenerate: () => void;
  onFeedback: (feedback: Feedback) => void;
  disableActions?: boolean;
}

function formatTime(date: string): string {
  return new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" }).format(new Date(date));
}

export default function ChatMessage({ message, isGenerating, onRegenerate, onFeedback, disableActions }: ChatMessageProps) {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const isUser = message.role === "user";
  const hasContent = message.content.length > 0;
  return (
    <article className={`group flex gap-3.5 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <div className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl ${isUser ? "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-300" : "bg-blue-600 text-white shadow-sm shadow-blue-600/20"}`}>
        {isUser ? <UserRound size={15} /> : <Bot size={16} />}
      </div>
      <div className={`min-w-0 max-w-[min(85%,680px)] ${isUser ? "items-end" : "items-start"} flex flex-col`}>
        <div className={`mb-1.5 flex items-center gap-2 text-[11px] text-slate-400 ${isUser ? "flex-row-reverse" : ""}`}>
          <span className="font-medium text-slate-600 dark:text-slate-300">{isUser ? "You" : "Nexus AI"}</span>
          <time dateTime={message.createdAt}>{formatTime(message.createdAt)}</time>
        </div>
        <div className={`message-bubble ${isUser ? "user-bubble" : "assistant-bubble"}`}>
          {!isUser && !hasContent && isGenerating ? (
            <div className="flex items-center gap-2 py-1 text-sm text-slate-400">
              <span className="typing-dots"><i /><i /><i /></span>
              <span>Thinking</span>
            </div>
          ) : isUser ? (
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          ) : (
            <>
              <div className="markdown-content">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeHighlight]}
                  components={{
                    pre({ children }) {
                      const code = String((children as ReactElement<{ children?: ReactNode }>).props?.children ?? "")
                        .replace(/\n$/, "");
                      const copied = copiedCode === code;
                      return (
                        <div className="code-frame">
                          <div className="code-header">
                            <span>Code</span>
                            <button
                              type="button"
                              className="code-copy"
                              onClick={() => {
                                void navigator.clipboard.writeText(code).then(() => {
                                  setCopiedCode(code);
                                  window.setTimeout(() => setCopiedCode(null), 1500);
                                }).catch((error: unknown) => console.error("Could not copy code.", error));
                              }}
                            >
                              {copied ? <Check size={13} /> : <Copy size={13} />}
                              {copied ? "Copied" : "Copy"}
                            </button>
                          </div>
                          <pre>{children}</pre>
                        </div>
                      );
                    },
                    a({ href, children }) {
                      return <a href={href} target="_blank" rel="noreferrer">{children}</a>;
                    },
                  }}
                >
                  {message.content}
                </ReactMarkdown>
                {isGenerating && hasContent && <span className="stream-cursor" aria-label="Generating" />}
              </div>
              {message.error && (
                <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700 dark:bg-red-950/40 dark:text-red-300">
                  Response interrupted: {message.error}
                </p>
              )}
            </>
          )}
        </div>
        {!isUser && hasContent && !isGenerating && (
          <MessageActions
            content={message.content}
            feedback={message.feedback}
            onRegenerate={onRegenerate}
            onFeedback={onFeedback}
            disabled={disableActions}
          />
        )}
      </div>
    </article>
  );
}
