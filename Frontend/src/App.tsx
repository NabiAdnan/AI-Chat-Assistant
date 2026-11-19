import { useEffect, useState } from "react";
import { X } from "lucide-react";
import ChatHeader from "./components/ChatHeader";
import ChatWindow from "./components/ChatWindow";
import Sidebar from "./components/Sidebar";
import { useChat } from "./hooks/useChat";

export default function App() {
  const chat = useChat();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [dark, setDark] = useState(() => localStorage.getItem("nexus-ai-theme") === "dark");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("nexus-ai-theme", dark ? "dark" : "light");
  }, [dark]);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        chat.createConversation();
      }
      if (event.key === "Escape") setSidebarOpen(false);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [chat.createConversation]);

  return (
    <div className="app-shell">
      <Sidebar
        conversations={chat.conversations}
        activeId={chat.activeId}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNewChat={chat.createConversation}
        onSelect={(id) => void chat.selectConversation(id)}
        onRename={chat.renameConversation}
        onDelete={(id) => void chat.deleteConversation(id)}
        demoMode={chat.demoMode}
      />
      <div className="main-panel">
        <ChatHeader
          title={chat.activeConversation?.title}
          tone={chat.tone}
          onToneChange={chat.setTone}
          dark={dark}
          onToggleTheme={() => setDark((value) => !value)}
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen((value) => !value)}
        />
        {chat.error && (
          <div role="alert" className="mx-4 mt-3 flex items-start justify-between gap-3 rounded-xl border border-red-200 bg-red-50 px-3.5 py-2.5 text-xs text-red-700 dark:border-red-900/70 dark:bg-red-950/30 dark:text-red-300 sm:mx-7">
            <span>{chat.error}</span>
            <button type="button" onClick={chat.clearError} aria-label="Dismiss error"><X size={15} /></button>
          </div>
        )}
        <ChatWindow
          messages={chat.messages}
          isGenerating={chat.isGenerating}
          onSend={chat.sendMessage}
          onStop={chat.stopGenerating}
          onRegenerate={chat.regenerate}
          onFeedback={chat.setFeedback}
        />
      </div>
    </div>
  );
}
