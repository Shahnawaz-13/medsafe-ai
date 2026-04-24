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
  Shield,
} from "lucide-react";
import { sendChatMessage } from "@/lib/api";
import Disclaimer         from "@/components/Disclaimer";
import { cn }             from "@/lib/utils";

// ── Types ─────────────────────────────────────────────────────────────
interface ChatMessage {
  id:        string;
  role:      "user" | "assistant";
  content:   string;
  timestamp: string;
  isError?:  boolean;
}

// ── Starter questions ─────────────────────────────────────────────────
const STARTER_QUESTIONS = [
  "Can I take ibuprofen with warfarin?",
  "Is it safe to drink alcohol with metformin?",
  "What happens if I mix aspirin and blood thinners?",
  "Can I take paracetamol with lisinopril?",
  "Is sertraline safe with tramadol?",
  "Can I take antacids with ciprofloxacin?",
];

// ── Helper ────────────────────────────────────────────────────────────
function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString("en-IN", {
    hour:   "2-digit",
    minute: "2-digit",
  });
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

const WELCOME_MESSAGE: ChatMessage = {
  id:        "welcome",
  role:      "assistant",
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

// ── Message bubble ────────────────────────────────────────────────────
function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 max-w-full",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center",
          "rounded-full mt-1",
          isUser ? "bg-indigo-600" : "bg-gray-100"
        )}
      >
        {isUser
          ? <User className="h-4 w-4 text-white" />
          : <Bot  className="h-4 w-4 text-gray-600" />
        }
      </div>

      {/* Message content */}
      <div
        className={cn(
          "flex flex-col max-w-[80%] sm:max-w-[70%]",
          isUser ? "items-end" : "items-start"
        )}
      >
        {/* Role label */}
        <p className="text-xs text-gray-400 mb-1 px-1">
          {isUser ? "You" : "RxChat AI"}
        </p>

        {/* Bubble */}
        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "bg-indigo-600 text-white rounded-tr-sm"
              : message.isError
              ? "bg-red-50 text-red-700 border border-red-200 rounded-tl-sm"
              : "bg-white text-gray-800 border border-gray-200 rounded-tl-sm shadow-sm",
          )}
        >
          {message.isError && (
            <div className="flex items-center gap-1.5 mb-2">
              <AlertCircle className="h-3.5 w-3.5 text-red-500" />
              <span className="text-xs font-semibold text-red-600">
                Error
              </span>
            </div>
          )}

          {/* Render content with basic markdown */}
          {message.content.split("\n").map((line, i) => {
            if (line.startsWith("**") && line.endsWith("**")) {
              return (
                <p key={i} className="font-semibold mt-2 mb-1">
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
              <p key={i} className="text-sm">{line}</p>
            );
          })}
        </div>

        {/* Timestamp */}
        <p className="text-xs text-gray-400 mt-1 px-1">
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
}

// ── Typing indicator ──────────────────────────────────────────────────
function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center
                      rounded-full bg-gray-100 mt-1">
        <Bot className="h-4 w-4 text-gray-600" />
      </div>
      <div className="flex flex-col items-start">
        <p className="text-xs text-gray-400 mb-1 px-1">RxChat AI</p>
        <div className="rounded-2xl rounded-tl-sm bg-white border
                        border-gray-200 px-4 py-3 shadow-sm">
          <div className="flex gap-1.5 items-center h-4">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="h-2 w-2 rounded-full bg-gray-400
                           animate-bounce"
                style={{ animationDelay: `${i * 150}ms` }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────
export default function ChatPage() {
  const [messages,   setMessages]   = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading,  setIsLoading]  = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef       = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // ── Send message ────────────────────────────────────────────────
  const sendMessage = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    // Add user message
    const userMsg: ChatMessage = {
      id:        generateId(),
      role:      "user",
      content:   trimmed,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    setIsLoading(true);

    // Build history for API
    const history = messages
      .filter((m) => m.id !== "welcome" && !m.isError)
      .map((m) => ({ role: m.role, content: m.content }));

    try {
      const response = await sendChatMessage(trimmed);

      const assistantMsg: ChatMessage = {
        id:        generateId(),
        role:      "assistant",
        content:   response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);

    } catch (err: any) {
      const errMsg: ChatMessage = {
        id:        generateId(),
        role:      "assistant",
        content:   err?.message ||
                   "I'm having trouble responding right now. " +
                   "Please try again or consult your pharmacist directly.",
        timestamp: new Date().toISOString(),
        isError:   true,
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  // ── Keyboard handler ────────────────────────────────────────────
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputValue);
    }
  };

  // ── Clear chat ──────────────────────────────────────────────────
  const handleClear = () => {
    setMessages([WELCOME_MESSAGE]);
    setInputValue("");
    inputRef.current?.focus();
  };

  // ── Render ──────────────────────────────────────────────────────
  return (
    <div className="flex h-[calc(100vh-64px)] flex-col bg-gray-50">

      {/* ── Header ──────────────────────────────────────────────── */}
      <div className="border-b border-gray-200 bg-white px-4 py-3">
        <div className="mx-auto flex max-w-3xl items-center
                        justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center
                            rounded-xl bg-indigo-600">
              <MessageCircle className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-base font-bold text-gray-900">
                RxChat
              </h1>
              <div className="flex items-center gap-1.5">
                <div className="h-2 w-2 rounded-full bg-green-400
                                animate-pulse" />
                <p className="text-xs text-gray-500">
                  Powered by Groq LLaMA AI
                </p>
              </div>
            </div>
          </div>

          <button
            onClick={handleClear}
            className="flex items-center gap-1.5 rounded-lg
                       border border-gray-200 px-3 py-1.5 text-xs
                       font-medium text-gray-600 hover:bg-gray-50
                       transition-colors"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Clear
          </button>
        </div>
      </div>

      {/* ── Messages area ───────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl px-4 py-6 space-y-5">

          {/* Messages */}
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {/* Typing indicator */}
          {isLoading && <TypingIndicator />}

          {/* Scroll anchor */}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* ── Starter questions ─────────────────────────────────────── */}
      {messages.length === 1 && !isLoading && (
        <div className="border-t border-gray-100 bg-white px-4 py-3">
          <div className="mx-auto max-w-3xl">
            <p className="text-xs font-medium text-gray-400 mb-2">
              Try asking:
            </p>
            <div className="flex flex-wrap gap-2">
              {STARTER_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="rounded-full border border-gray-200
                             bg-gray-50 px-3 py-1.5 text-xs
                             font-medium text-gray-600
                             hover:bg-indigo-50 hover:border-indigo-200
                             hover:text-indigo-700 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Input area ────────────────────────────────────────────── */}
      <div className="border-t border-gray-200 bg-white px-4 py-3">
        <div className="mx-auto max-w-3xl">
          {/* Disclaimer compact */}
          <Disclaimer compact className="mb-3" />

          <div className="flex gap-2 items-end">
            <div className="flex-1 rounded-xl border border-gray-200
                            bg-gray-50 focus-within:border-indigo-400
                            focus-within:bg-white transition-colors">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about your medications... (Enter to send)"
                rows={1}
                disabled={isLoading}
                className="w-full resize-none bg-transparent px-4 py-3
                           text-sm text-gray-800 outline-none
                           placeholder:text-gray-400 max-h-32
                           min-h-11"
                style={{ height: "auto" }}
                onInput={(e) => {
                  const el = e.currentTarget;
                  el.style.height = "auto";
                  el.style.height =
                    Math.min(el.scrollHeight, 128) + "px";
                }}
              />
            </div>

            <button
              onClick={() => sendMessage(inputValue)}
              disabled={!inputValue.trim() || isLoading}
              className={cn(
                "flex h-11 w-11 shrink-0 items-center justify-center",
                "rounded-xl transition-all duration-200",
                inputValue.trim() && !isLoading
                  ? "bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm"
                  : "bg-gray-100 text-gray-400 cursor-not-allowed"
              )}
            >
              {isLoading
                ? <Loader2 className="h-4 w-4 animate-spin" />
                : <Send    className="h-4 w-4" />
              }
            </button>
          </div>

          <p className="mt-2 text-center text-xs text-gray-400">
            Press Enter to send · Shift+Enter for new line ·
            For urgent questions, call your pharmacist directly
          </p>
        </div>
      </div>
    </div>
  );
}