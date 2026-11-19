import { Check, ChevronDown } from "lucide-react";
import { useState } from "react";
import type { Tone } from "../types/chat";

const tones: { name: Tone; description: string }[] = [
  { name: "Professional", description: "Clear and structured" },
  { name: "Casual", description: "Friendly and relaxed" },
  { name: "Concise", description: "Short and direct" },
];

interface ToneSelectorProps {
  value: Tone;
  onChange: (tone: Tone) => void;
}

export default function ToneSelector({ value, onChange }: ToneSelectorProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative">
      <button
        type="button"
        className="control-button gap-2"
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        <span className="hidden text-[11px] text-slate-400 sm:inline">Tone</span>
        <span className="text-xs font-medium text-slate-700 dark:text-slate-200">{value}</span>
        <ChevronDown size={14} className="text-slate-400" />
      </button>
      {open && (
        <>
          <button className="fixed inset-0 z-10 cursor-default" aria-label="Close tone menu" onClick={() => setOpen(false)} />
          <div className="menu-panel absolute right-0 top-12 z-20 w-56 p-1.5" role="listbox" aria-label="Response tone">
            {tones.map((tone) => (
              <button
                type="button"
                key={tone.name}
                role="option"
                aria-selected={value === tone.name}
                className="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left hover:bg-slate-50 dark:hover:bg-slate-800"
                onClick={() => {
                  onChange(tone.name);
                  setOpen(false);
                }}
              >
                <span>
                  <span className="block text-sm font-medium">{tone.name}</span>
                  <span className="mt-0.5 block text-xs text-slate-400">{tone.description}</span>
                </span>
                {value === tone.name && <Check size={15} className="text-blue-600" />}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
