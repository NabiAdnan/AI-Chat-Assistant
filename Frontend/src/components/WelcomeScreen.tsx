import { ArrowUpRight, Braces, FileText, Lightbulb, MessageCircleQuestion } from "lucide-react";

const suggestions = [
  { icon: Lightbulb, label: "Explain a technical concept", prompt: "Explain a technical concept in a simple, memorable way." },
  { icon: Braces, label: "Help me write code", prompt: "Help me write code for a project I'm working on." },
  { icon: MessageCircleQuestion, label: "Prepare me for an interview", prompt: "Help me prepare for an upcoming interview." },
  { icon: FileText, label: "Summarize a document", prompt: "Help me summarize a document. I'll share it with you." },
];

interface WelcomeScreenProps {
  onSuggestion: (prompt: string) => void;
}

export default function WelcomeScreen({ onSuggestion }: WelcomeScreenProps) {
  return (
    <div className="mx-auto flex min-h-full w-full max-w-[760px] flex-col justify-center px-5 pb-10 pt-12 sm:px-8">
      <div className="mb-9 text-center">
        <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400">
          <span className="nexus-mark"><i /><i /><i /><i /></span>
        </div>
        <h1 className="text-[30px] font-semibold tracking-[-0.045em] text-slate-900 dark:text-white sm:text-[36px]">
          How can I help you today?
        </h1>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 sm:text-base">Ask anything. Explore ideas. Get things done.</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {suggestions.map(({ icon: Icon, label, prompt }) => (
          <button
            type="button"
            key={label}
            className="suggestion-card group text-left"
            onClick={() => onSuggestion(prompt)}
          >
            <span className="mb-5 flex h-9 w-9 items-center justify-center rounded-xl bg-slate-50 text-slate-500 transition-colors group-hover:bg-blue-50 group-hover:text-blue-600 dark:bg-slate-800 dark:text-slate-400 dark:group-hover:bg-blue-500/10 dark:group-hover:text-blue-300">
              <Icon size={17} strokeWidth={1.8} />
            </span>
            <span className="flex items-center justify-between gap-3 text-[13px] font-medium text-slate-700 dark:text-slate-200">
              {label}
              <ArrowUpRight size={15} className="text-slate-300 transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-blue-500" />
            </span>
          </button>
        ))}
      </div>
      <div className="mt-7 flex items-center justify-center gap-2 text-[11px] text-slate-400">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Ready whenever you are
      </div>
    </div>
  );
}
