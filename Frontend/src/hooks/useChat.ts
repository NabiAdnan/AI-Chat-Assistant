import { useCallback, useEffect, useRef, useState } from "react";
import * as api from "../services/chatService";
import * as demo from "../services/demoService";
import type { ChatMessage, Conversation, Feedback, Tone } from "../types/chat";

const demoMode = import.meta.env.VITE_DEMO_MODE !== "false";

function makeId(): string {
  return crypto.randomUUID();
}

function sortConversations(conversations: Conversation[]): Conversation[] {
  return [...conversations].sort((a, b) => Date.parse(b.updatedAt) - Date.parse(a.updatedAt));
}

export function useChat() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [tone, setTone] = useState<Tone>("Professional");
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const conversationsRef = useRef(conversations);
  conversationsRef.current = conversations;

  useEffect(() => {
    let cancelled = false;
    const load = demoMode ? Promise.resolve(demo.loadDemoConversations()) : api.getConversations();
    load.then((items) => {
      if (cancelled) return;
      const sorted = sortConversations(items);
      setConversations(sorted);
      setActiveId(sorted[0]?.id ?? null);
    }).catch((reason: unknown) => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : "Could not load conversations.");
    });
    return () => {
      cancelled = true;
      controllerRef.current?.abort();
    };
  }, []);

  const commit = useCallback((next: Conversation[]) => {
    const sorted = sortConversations(next);
    conversationsRef.current = sorted;
    setConversations(sorted);
    if (demoMode) demo.saveDemoConversations(sorted);
  }, []);

  const createConversation = useCallback(() => {
    controllerRef.current?.abort();
    controllerRef.current = null;
    setIsGenerating(false);
    setError(null);
    setActiveId(null);
  }, []);

  const selectConversation = useCallback(async (id: string) => {
    controllerRef.current?.abort();
    controllerRef.current = null;
    setIsGenerating(false);
    setError(null);
    setActiveId(id);
    if (demoMode) return;
    try {
      const loaded = await api.getConversation(id);
      commit(conversationsRef.current.map((item) => item.id === id ? loaded : item));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load this conversation.");
    }
  }, [commit]);

  const updateConversation = useCallback((id: string, update: (conversation: Conversation) => Conversation) => {
    commit(conversationsRef.current.map((conversation) => conversation.id === id ? update(conversation) : conversation));
  }, [commit]);

  const generate = useCallback(async (prompt: string, existingId?: string, assistantId?: string) => {
    const message = prompt.trim();
    if (!message || controllerRef.current) return;
    setError(null);
    const conversationId = existingId ?? makeId();
    const existing = conversationsRef.current.find((item) => item.id === conversationId);
    const userMessage: ChatMessage = demo.createDemoMessage("user", message);
    const newAssistant: ChatMessage = {
      id: assistantId ?? makeId(),
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString(),
    };
    const initialMessages = existing ? [...existing.messages] : [];
    if (assistantId) {
      const targetIndex = initialMessages.findIndex((item) => item.id === assistantId);
      if (targetIndex >= 0) initialMessages[targetIndex] = { ...newAssistant, content: "" };
    } else {
      initialMessages.push(userMessage, newAssistant);
    }
    const conversation: Conversation = {
      id: conversationId,
      title: existing?.title ?? message.slice(0, 40) + (message.length > 40 ? "…" : ""),
      updatedAt: new Date().toISOString(),
      messages: initialMessages,
    };
    const withoutCurrent = conversationsRef.current.filter((item) => item.id !== conversationId);
    commit([conversation, ...withoutCurrent]);
    setActiveId(conversationId);

    if (demoMode) {
      const reply = demo.makeDemoReply(message, tone);
      updateConversation(conversationId, (current) => ({
        ...current,
        updatedAt: new Date().toISOString(),
        messages: current.messages.map((item) => item.id === newAssistant.id ? { ...item, content: reply } : item),
      }));
      return;
    }

    const controller = new AbortController();
    controllerRef.current = controller;
    setIsGenerating(true);
    try {
      await api.streamChat(
        { conversation_id: conversationId, message, tone },
        (chunk) => updateConversation(conversationId, (current) => ({
          ...current,
          updatedAt: new Date().toISOString(),
          messages: current.messages.map((item) => item.id === newAssistant.id
            ? { ...item, content: item.content + chunk }
            : item),
        })),
        controller.signal,
        assistantId ? "/chat/regenerate" : "/chat",
      );
    } catch (reason) {
      if (!controller.signal.aborted) {
        const detail = reason instanceof Error ? reason.message : "The response could not be generated.";
        updateConversation(conversationId, (current) => ({
          ...current,
          messages: current.messages.map((item) => item.id === newAssistant.id
            ? { ...item, error: detail }
            : item),
        }));
        setError(detail);
      }
    } finally {
      if (controllerRef.current === controller) {
        controllerRef.current = null;
        setIsGenerating(false);
      }
    }
  }, [commit, tone, updateConversation]);

  const sendMessage = useCallback((prompt: string) => {
    void generate(prompt, activeId ?? undefined);
  }, [activeId, generate]);

  const regenerate = useCallback((assistantId: string) => {
    const conversation = conversationsRef.current.find((item) => item.id === activeId);
    if (!conversation) return;
    const index = conversation.messages.findIndex((item) => item.id === assistantId);
    const previousUser = conversation.messages.slice(0, index).reverse().find((item) => item.role === "user");
    if (previousUser) void generate(previousUser.content, conversation.id, assistantId);
  }, [activeId, generate]);

  const stopGenerating = useCallback(() => {
    controllerRef.current?.abort();
    controllerRef.current = null;
    setIsGenerating(false);
  }, []);

  const renameConversation = useCallback((id: string, title: string) => {
    const cleanTitle = title.trim();
    if (!cleanTitle) return;
    updateConversation(id, (conversation) => ({ ...conversation, title: cleanTitle }));
    if (!demoMode) {
      void api.renameConversation(id, cleanTitle).catch((reason: unknown) => {
        console.error("Could not persist conversation rename:", reason);
      });
    }
  }, [updateConversation]);

  const deleteConversation = useCallback(async (id: string) => {
    setError(null);
    if (!demoMode) {
      try {
        await api.deleteConversation(id);
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : "Could not delete conversation.");
        return;
      }
    }
    const remaining = conversationsRef.current.filter((item) => item.id !== id);
    if (activeId === id) {
      controllerRef.current?.abort();
      controllerRef.current = null;
      setIsGenerating(false);
    }
    commit(remaining);
    if (activeId === id) setActiveId(remaining[0]?.id ?? null);
  }, [activeId, commit]);

  const setFeedback = useCallback((messageId: string, feedback: Feedback) => {
    if (!activeId) return;
    updateConversation(activeId, (conversation) => ({
      ...conversation,
      messages: conversation.messages.map((message) => message.id === messageId
        ? { ...message, feedback: message.feedback === feedback ? undefined : feedback }
        : message),
    }));
  }, [activeId, updateConversation]);

  const activeConversation = conversations.find((item) => item.id === activeId) ?? null;
  const messages = activeConversation?.messages ?? [];

  return {
    conversations,
    activeConversation,
    activeId,
    messages,
    tone,
    setTone,
    isGenerating,
    error,
    clearError: () => setError(null),
    createConversation,
    selectConversation,
    sendMessage,
    regenerate,
    stopGenerating,
    renameConversation,
    deleteConversation,
    setFeedback,
    demoMode,
  };
}
