import { Ellipsis, MessageSquarePlus, MoreHorizontal, Pencil, Search, Trash2, X } from "lucide-react";
import { useMemo, useState } from "react";
import type { Conversation } from "../types/chat";

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  open: boolean;
  onClose: () => void;
  onNewChat: () => void;
  onSelect: (id: string) => void;
  onRename: (id: string, title: string) => void;
  onDelete: (id: string) => void;
  demoMode: boolean;
}

function dayGroup(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const thatDay = new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
  const diff = Math.round((today - thatDay) / 86_400_000);
  if (diff <= 0) return "Today";
  if (diff === 1) return "Yesterday";
  if (diff < 7) return "Previous 7 days";
  return "Older";
}

export default function Sidebar({
  conversations,
  activeId,
  open,
  onClose,
  onNewChat,
  onSelect,
  onRename,
  onDelete,
  demoMode,
}: SidebarProps) {
  const [query, setQuery] = useState("");
  const [menuId, setMenuId] = useState<string | null>(null);
  const groups = useMemo(() => {
    const filtered = conversations.filter((item) => item.title.toLowerCase().includes(query.trim().toLowerCase()));
    return ["Today", "Yesterday", "Previous 7 days", "Older"].map((label) => ({
      label,
      items: filtered.filter((item) => dayGroup(item.updatedAt) === label),
    })).filter((group) => group.items.length > 0);
  }, [conversations, query]);

  function rename(item: Conversation) {
    const title = window.prompt("Rename conversation", item.title);
    if (title?.trim()) onRename(item.id, title);
    setMenuId(null);
  }

  return (
    <>
      {open && <button className="sidebar-backdrop md:hidden" onClick={onClose} aria-label="Close sidebar" />}
      <aside className={`sidebar ${open ? "sidebar-open" : "sidebar-closed"}`}>
        <div className="flex h-[68px] items-center justify-between px-5">
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-[11px] bg-blue-600 text-white shadow-sm shadow-blue-600/25">
              <span className="nexus-mark nexus-mark-white"><i /><i /><i /><i /></span>
            </span>
            <span className="text-[15px] font-semibold tracking-[-0.03em] text-slate-900 dark:text-white">Nexus <span className="font-normal text-slate-400">AI</span></span>
          </div>
          <button type="button" className="icon-button md:hidden" onClick={onClose} aria-label="Close sidebar"><X size={17} /></button>
        </div>

        <div className="px-3 pt-3">
          <button
            type="button"
            className="new-chat-button"
            onClick={() => {
              onNewChat();
              onClose();
            }}
          >
            <MessageSquarePlus size={16} strokeWidth={1.8} />
            <span>New chat</span>
            <span className="new-chat-shortcut">⌘ K</span>
          </button>
          <label className="search-field mt-3">
            <Search size={15} className="shrink-0 text-slate-400" />
            <input
              type="search"
              placeholder="Search conversations"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              aria-label="Search conversations"
            />
            {query && <button type="button" aria-label="Clear search" onClick={() => setQuery("")}><X size={14} /></button>}
          </label>
        </div>

        <div className="sidebar-scroll mt-6 flex-1 px-3">
          {groups.length === 0 ? (
            <div className="px-2 py-8 text-center text-xs text-slate-400">{query ? "No matching conversations" : "Your conversations will appear here"}</div>
          ) : groups.map((group) => (
            <section key={group.label} className="mb-5">
              <h2 className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-400">{group.label}</h2>
              <div className="space-y-0.5">
                {group.items.map((item) => (
                  <div key={item.id} className={`conversation-row ${activeId === item.id ? "conversation-active" : ""}`}>
                    <button
                      type="button"
                      className="min-w-0 flex-1 truncate px-2.5 py-2 text-left text-[12.5px]"
                      onClick={() => {
                        onSelect(item.id);
                        onClose();
                      }}
                      title={item.title}
                    >
                      {item.title}
                    </button>
                    <button type="button" className="conversation-menu-button" onClick={() => setMenuId(menuId === item.id ? null : item.id)} aria-label={`Options for ${item.title}`}>
                      <MoreHorizontal size={16} />
                    </button>
                    {menuId === item.id && (
                      <>
                        <button className="fixed inset-0 z-10 cursor-default" aria-label="Close conversation menu" onClick={() => setMenuId(null)} />
                        <div className="menu-panel absolute right-1 top-9 z-20 w-40 p-1">
                          <button type="button" className="menu-item" onClick={() => rename(item)}><Pencil size={14} /> Rename</button>
                          <button type="button" className="menu-item text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/30" onClick={() => { onDelete(item.id); setMenuId(null); }}><Trash2 size={14} /> Delete</button>
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>

        <div className="border-t border-slate-200/75 p-3 dark:border-slate-800">
          {demoMode && <div className="mb-2 rounded-lg bg-amber-50 px-2.5 py-2 text-[10px] leading-relaxed text-amber-700 dark:bg-amber-950/30 dark:text-amber-300">Demo mode · replies are sample content</div>}
          <div className="profile-button">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#dce8f8] text-[11px] font-semibold text-[#466185] dark:bg-slate-700 dark:text-slate-200">AF</span>
            <span className="min-w-0 flex-1 text-left">
              <span className="block truncate text-xs font-medium text-slate-700 dark:text-slate-200">Alex Morgan</span>
              <span className="mt-0.5 block text-[10px] text-slate-400">{demoMode ? "Personal workspace" : "Connected to API"}</span>
            </span>
            <Ellipsis size={17} className="text-slate-400" />
          </div>
        </div>
      </aside>
    </>
  );
}
