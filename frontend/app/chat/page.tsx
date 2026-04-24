// app/chat/page.tsx
"use client";

import {
  useState,
  useRef,
  useEffect,
  KeyboardEvent,
} from "react";
import {
  Send,
  Bot,
  User,
  MessageCircle,
  Loader2,
  Trash2,
  AlertCircle,
} from "lucide-react";
import { sendChatMessage } from "@/lib/api";
import Disclaimer from "@/components/Disclaimer";
import { cn } from "@/lib/utils";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isError?: boolean;
}

const STARTER_QUESTIONS = [
  "Can I take ibuprofen with warfarin?",
  "Is it safe to drink alcohol with metformin?",
  "What happens if I mix aspirin and blood thinners?",
  "Can I take paracetamol with lisinopril?",
  "Is sertraline safe with tramadol?",
  "Can I take antacids with ciprofloxacin?",
];

function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

const WELCOME_MESSAGE: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content: [
    "Hello! I'm RxChat, your AI medication safety assistant.",
    "",
    "I can help you understand drug interactions, explain what symptoms to watch for, and answer general questions about medication safety.",
    "",
    "**What I can help with:**",
    "• Drug-drug interaction questions",
    "• What symptoms to watch for",
    "• General medication safety information",
    "• When to see a doctor or pharmacist",
    "",
    "Remember: I provide general information only. Always consult your doctor or pharmacist for personal medical decisions.",
    "",
    "What would you like to know?",
  ].join("\n"),
  timestamp: new Date().toISOString(),
};

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex max-w-full gap-3",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      <div
        className={cn(
          "mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-indigo-600" : "bg-gray-100"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4 text-white" />
        ) : (
          <Bot className="h-4 w-4 text-gray-600" />
        )}
      </div>

      <div
        className={cn(
          "flex max-w-[80%] flex-col sm:max-w-[70%]",
          isUser ? "items-end" : "items-start"
        )}
      >
        <p className="mb-1 px-1 text-xs text-gray-400">
          {isUser ? "You" : "RxChat AI"}
        </p>

        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "rounded-tr-sm bg-indigo-600 text-white"
              : message.isError
              ? "rounded-tl-sm border border-red-200 bg-red-50 text-red-700"
              : "rounded-tl-sm border border-gray-200 bg-white text-gray-800 shadow-sm"
          )}
        >
          {message.isError && (
            <div className="mb-2 flex items-center gap-1.5">
              <AlertCircle className="h-3.5 w-3.5 text-red-500" />
              <span className="text-xs font-semibold text-red-600">
                Error
              </span>
            </div>
          )}

          {message.content.split("\n").map((line, i) => {
            if (line.startsWith("**") && line.endsWith("**")) {
              return (
                <p key={i} className="mb-1 mt-2 font-semibold">
                  {line.slice(2, -2)}
                </p>
              );
            }

            if (line.startsWith("• ")) {
              return (
                <p key={i} className="flex gap-1.5 text-sm">
                  <span>•</span>
                  <span>{line.slice(2)}</span>
                </p>
              );
            }

            if (line === "") {
              return <div key={i} className="h-1" />;
            }

            return (
              <p key={i} className="text-sm">
                {line}
              </p>
            );
          })}
        </div>

        <p className="mt-1 px-1 text-xs text-gray-400">
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-100">
        <Bot className="h-4 w-4 text-gray-600" />
      </div>

      <div className="flex flex-col items-start">
        <p className="mb-1 px-1 text-xs text-gray-400">RxChat AI</p>

        <div className="rounded-2xl rounded-tl-sm border border-gray-200 bg-white px-4 py-3 shadow-sm">
          <div className="flex h-4 items-center gap-1.5">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="h-2 w-2 animate-bounce rounded-full bg-gray-400"
                style={{ animationDelay: `${i * 150}ms` }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const sendMessage = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    const userMsg: ChatMessage = {
      id: generateId(),
      role: "user",
      content: trimmed,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await sendChatMessage(trimmed);

      const assistantMsg: ChatMessage = {
        id: generateId(),
        role: "assistant",
        content: response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : "I'm having trouble responding right now. Please try again or consult your pharmacist directly.";

      const errMsg: ChatMessage = {
        id: generateId(),
        role: "assistant",
        content: errorMessage,
        timestamp: new Date().toISOString(),
        isError: true,
      };

      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputValue);
    }
  };

  const handleClear = () => {
    setMessages([WELCOME_MESSAGE]);
    setInputValue("");
    inputRef.current?.focus();
  };

  return (
    <div className="flex h-[calc(100vh-64px)] flex-col bg-gray-50">
      <div className="border-b border-gray-200 bg-white px-4 py-3">
        <div className="mx-auto flex max-w-3xl items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600">
              <MessageCircle className="h-5 w-5 text-white" />
            </div>

            <div>
              <h1 className="text-base font-bold text-gray-900">RxChat</h1>
              <div className="flex items-center gap-1.5">
                <div className="h-2 w-2 animate-pulse rounded-full bg-green-400" />
                <p className="text-xs text-gray-500">
                  Powered by Groq LLaMA AI
                </p>
              </div>
            </div>
          </div>

          <button
            type="button"
            aria-label="Clear chat"
            onClick={handleClear}
            className="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-50"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Clear
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl space-y-5 px-4 py-6">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {isLoading && <TypingIndicator />}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {messages.length === 1 && !isLoading && (
        <div className="border-t border-gray-100 bg-white px-4 py-3">
          <div className="mx-auto max-w-3xl">
            <p className="mb-2 text-xs font-medium text-gray-400">
              Try asking:
            </p>

            <div className="flex flex-wrap gap-2">
              {STARTER_QUESTIONS.map((q) => (
                <button
                  key={q}
                  type="button"
                  aria-label={`Ask: ${q}`}
                  onClick={() => sendMessage(q)}
                  className="rounded-full border border-gray-200 bg-gray-50 px-3 py-1.5 text-xs font-medium text-gray-600 transition-colors hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="border-t border-gray-200 bg-white px-4 py-3">
        <div className="mx-auto max-w-3xl">
          <Disclaimer compact className="mb-3" />

          <div className="flex items-end gap-2">
            <div className="flex-1 rounded-xl border border-gray-200 bg-gray-50 transition-colors focus-within:border-indigo-400 focus-within:bg-white">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about your medications... (Enter to send)"
                rows={1}
                disabled={isLoading}
                aria-label="Chat message input"
                className="max-h-32 min-h-11 w-full resize-none bg-transparent px-4 py-3 text-sm text-gray-800 outline-none placeholder:text-gray-400"
                style={{ height: "auto" }}
                onInput={(e) => {
                  const el = e.currentTarget;
                  el.style.height = "auto";
                  el.style.height = `${Math.min(el.scrollHeight, 128)}px`;
                }}
              />
            </div>

            <button
              type="button"
              aria-label="Send message"
              onClick={() => sendMessage(inputValue)}
              disabled={!inputValue.trim() || isLoading}
              className={cn(
                "flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-all duration-200",
                inputValue.trim() && !isLoading
                  ? "bg-indigo-600 text-white shadow-sm hover:bg-indigo-700"
                  : "cursor-not-allowed bg-gray-100 text-gray-400"
              )}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </div>

          <p className="mt-2 text-center text-xs text-gray-400">
            Press Enter to send · Shift+Enter for new line · For urgent
            questions, call your pharmacist directly
          </p>
        </div>
      </div>
    </div>
  );
}