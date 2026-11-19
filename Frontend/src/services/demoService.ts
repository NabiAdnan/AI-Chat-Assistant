import type { ChatMessage, Conversation, Tone } from "../types/chat";

const storageKey = "nexus-ai-demo-conversations";
const now = Date.now();

const seedConversations: Conversation[] = [
  {
    id: "demo-product-launch",
    title: "Product launch checklist",
    updatedAt: new Date(now - 1000 * 60 * 18).toISOString(),
    messages: [
      {
        id: "demo-product-user",
        role: "user",
        content: "Help me put together a product launch checklist.",
        createdAt: new Date(now - 1000 * 60 * 20).toISOString(),
      },
      {
        id: "demo-product-assistant",
        role: "assistant",
        content:
          "A strong launch starts with a clear owner for every workstream. Here's a practical checklist:\n\n- **Positioning:** confirm audience, value proposition, and launch messaging.\n- **Product readiness:** test critical paths, analytics, support docs, and rollback plans.\n- **Go-to-market:** align the website, email, social, and sales enablement.\n- **Launch day:** monitor adoption, errors, and customer feedback in one shared channel.\n\nWould you like me to turn this into a timeline with owners and due dates?",
        createdAt: new Date(now - 1000 * 60 * 19).toISOString(),
      },
    ],
  },
  {
    id: "demo-typescript",
    title: "Understanding TypeScript generics",
    updatedAt: new Date(now - 1000 * 60 * 60 * 26).toISOString(),
    messages: [
      {
        id: "demo-types-user",
        role: "user",
        content: "Can you explain TypeScript generics simply?",
        createdAt: new Date(now - 1000 * 60 * 60 * 27).toISOString(),
      },
      {
        id: "demo-types-assistant",
        role: "assistant",
        content:
          "Think of a **generic** as a reusable placeholder for a type. It lets a function work with different types while keeping the relationship between its input and output:\n\n```ts\nfunction first<T>(items: T[]): T | undefined {\n  return items[0];\n}\n\nconst name = first([\"Ada\", \"Grace\"]); // string | undefined\n```\n\nHere, `T` is inferred as `string`. You get flexibility without giving up type safety.",
        createdAt: new Date(now - 1000 * 60 * 60 * 26).toISOString(),
      },
    ],
  },
  {
    id: "demo-weekly",
    title: "Weekly planning ideas",
    updatedAt: new Date(now - 1000 * 60 * 60 * 24 * 4).toISOString(),
    messages: [
      {
        id: "demo-weekly-user",
        role: "user",
        content: "How do I make weekly planning feel less overwhelming?",
        createdAt: new Date(now - 1000 * 60 * 60 * 24 * 4).toISOString(),
      },
      {
        id: "demo-weekly-assistant",
        role: "assistant",
        content:
          "Try a **20-minute weekly reset**: capture everything on your mind, choose three meaningful outcomes, and block time for just the first steps. Leave some unscheduled space so the plan can flex when the week changes.",
        createdAt: new Date(now - 1000 * 60 * 60 * 24 * 4).toISOString(),
      },
    ],
  },
];

export function loadDemoConversations(): Conversation[] {
  try {
    const saved = localStorage.getItem(storageKey);
    return saved ? (JSON.parse(saved) as Conversation[]) : seedConversations;
  } catch (error) {
    console.error("Could not read demo conversations from local storage.", error);
    return seedConversations;
  }
}

export function saveDemoConversations(conversations: Conversation[]): void {
  try {
    localStorage.setItem(storageKey, JSON.stringify(conversations));
  } catch (error) {
    console.error("Could not save demo conversations to local storage.", error);
  }
}

export function makeDemoReply(prompt: string, tone: Tone): string {
  const cleanPrompt = prompt.trim();
  if (/\b(code|typescript|javascript|python|function)\b/i.test(cleanPrompt)) {
    return `Let's work through it together. For **${cleanPrompt.replace(/[?.!]+$/, "")}**, start by defining the expected input and output, then handle the simplest case before adding edge cases.\n\n\`\`\`ts\nfunction solve(input: string): string {\n  return input.trim();\n}\n\`\`\`\n\nThis is a demo response in ${tone.toLowerCase()} tone. Connect the FastAPI service to enable live AI answers.`;
  }
  if (/\b(interview|prepare|practice)\b/i.test(cleanPrompt)) {
    return `A useful way to prepare is to pair a clear story with a specific result:\n\n1. Set the context briefly.\n2. Explain the decision or action you took.\n3. Share what changed and what you learned.\n\nThis is a demo response in ${tone.toLowerCase()} tone. Connect the FastAPI service to enable live AI answers.`;
  }
  return `Here’s a good place to start: break **${cleanPrompt.replace(/[?.!]+$/, "")}** into the main goal, the important constraints, and one concrete next step. From there, you can build a clear plan and refine it as you learn more.\n\nThis is a demo response in ${tone.toLowerCase()} tone. Connect the FastAPI service to enable live AI answers.`;
}

export function createDemoMessage(role: ChatMessage["role"], content: string): ChatMessage {
  return {
    id: `message-${crypto.randomUUID()}`,
    role,
    content,
    createdAt: new Date().toISOString(),
  };
}
