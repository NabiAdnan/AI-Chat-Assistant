import { Check, Copy, RotateCw, ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";
import type { Feedback } from "../types/chat";

interface MessageActionsProps {
  content: string;
  feedback?: Feedback;
  onRegenerate: () => void;
  onFeedback: (feedback: Feedback) => void;
  disabled?: boolean;
}

export default function MessageActions({ content, feedback, onRegenerate, onFeedback, disabled }: MessageActionsProps) {
  const [copied, setCopied] = useState(false);

  async function copyResponse() {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch (error) {
      console.error("Could not copy this response.", error);
    }
  }

  return (
    <div className="message-actions mt-2 flex items-center gap-1">
      <button type="button" className="action-button" onClick={() => void copyResponse()} aria-label={copied ? "Copied" : "Copy response"} title={copied ? "Copied!" : "Copy"}>
        {copied ? <Check size={14} className="text-emerald-600" /> : <Copy size={14} />}
        <span>{copied ? "Copied!" : ""}</span>
      </button>
      <button type="button" className="action-button" onClick={onRegenerate} disabled={disabled} aria-label="Regenerate response" title="Regenerate">
        <RotateCw size={14} />
      </button>
      <span className="mx-1 h-3.5 w-px bg-slate-200 dark:bg-slate-700" />
      <button type="button" className={`action-button ${feedback === "up" ? "text-blue-600" : ""}`} onClick={() => onFeedback("up")} aria-label="Helpful" title="Helpful">
        <ThumbsUp size={14} />
      </button>
      <button type="button" className={`action-button ${feedback === "down" ? "text-blue-600" : ""}`} onClick={() => onFeedback("down")} aria-label="Not helpful" title="Not helpful">
        <ThumbsDown size={14} />
      </button>
    </div>
  );
}
