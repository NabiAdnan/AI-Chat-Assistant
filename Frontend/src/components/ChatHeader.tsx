import { Menu, Moon, PanelLeftClose, PanelLeftOpen, Sun } from "lucide-react";
import ToneSelector from "./ToneSelector";
import type { Tone } from "../types/chat";

interface ChatHeaderProps {
  title?: string;
  tone: Tone;
  onToneChange: (tone: Tone) => void;
  dark: boolean;
  onToggleTheme: () => void;
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export default function ChatHeader({
  title,
  tone,
  onToneChange,
  dark,
  onToggleTheme,
  sidebarOpen,
  onToggleSidebar,
}: ChatHeaderProps) {
  return (
    <header className="flex h-[68px] shrink-0 items-center justify-between border-b border-slate-200/75 bg-white/90 px-4 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/90 sm:px-7">
      <div className="flex min-w-0 items-center gap-3">
        <button type="button" className="icon-button" onClick={onToggleSidebar} aria-label="Toggle sidebar">
          <span className="hidden sm:inline">{sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}</span>
          <span className="sm:hidden"><Menu size={19} /></span>
        </button>
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold text-slate-800 dark:text-slate-100">{title || "New conversation"}</div>
          <div className="mt-0.5 text-[11px] text-slate-400">Your thoughtful AI workspace</div>
        </div>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <ToneSelector value={tone} onChange={onToneChange} />
        <button type="button" className="icon-button" onClick={onToggleTheme} aria-label={`Switch to ${dark ? "light" : "dark"} theme`}>
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}
