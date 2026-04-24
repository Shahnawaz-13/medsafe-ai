// components/Navbar.tsx
"use client";
import Link      from "next/link";
import { usePathname } from "next/navigation";
import { useState }    from "react";
import {
  Menu, X, Shield, History,
  Upload, MessageCircle,
} from "lucide-react";
import { UserButton, SignedIn, SignedOut } from "@clerk/nextjs";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  {
    href:  "/check",
    label: "Check Drugs",
    icon:  Shield,
    desc:  "Check interactions",
  },
  {
    href:  "/chat",
    label: "RxChat",
    icon:  MessageCircle,
    desc:  "Ask AI questions",
  },
  {
    href:  "/history",
    label: "History",
    icon:  History,
    desc:  "Past checks",
  },
  {
    href:  "/upload",
    label: "Upload Rx",
    icon:  Upload,
    desc:  "Scan prescription",
  },
];

export default function Navbar() {
  const pathname = usePathname();
  const [open,   setOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 w-full border-b
                    border-gray-100 bg-white/95 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center
                      justify-between px-4 sm:px-6 lg:px-8">

        {/* ── Logo ──────────────────────────────────────────────── */}
        <Link
          href="/"
          className="flex items-center gap-2.5 shrink-0"
          onClick={() => setOpen(false)}
        >
          <div className="flex h-9 w-9 items-center justify-center
                          rounded-xl bg-indigo-600 shadow-sm">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <div className="flex items-baseline gap-0.5">
            <span className="text-xl font-bold text-indigo-700">
              MedSafe
            </span>
            <span className="text-xl font-bold text-teal-600">
              AI
            </span>
          </div>
        </Link>

        {/* ── Desktop nav links ──────────────────────────────────── */}
        <div className="hidden md:flex items-center gap-0.5">
          {NAV_LINKS.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-1.5 rounded-lg px-3.5",
                  "py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </div>

        {/* ── Desktop auth ───────────────────────────────────────── */}
        <div className="hidden md:flex items-center gap-3">
          <SignedOut>
            <Link
              href="/sign-in"
              className="text-sm font-medium text-gray-600
                         hover:text-gray-900 transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/sign-up"
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm
                         font-semibold text-white hover:bg-indigo-700
                         transition-colors shadow-sm"
            >
              Get Started
            </Link>
          </SignedOut>
          <SignedIn>
            <UserButton/>
          </SignedIn>
        </div>

        {/* ── Mobile hamburger ───────────────────────────────────── */}
        <button
          onClick={() => setOpen(!open)}
          className="md:hidden rounded-lg p-2 text-gray-600
                     hover:bg-gray-100 transition-colors"
          aria-label="Toggle menu"
        >
          {open
            ? <X    className="h-5 w-5" />
            : <Menu className="h-5 w-5" />
          }
        </button>
      </div>

      {/* ── Mobile menu ────────────────────────────────────────────── */}
      {open && (
        <div className="md:hidden border-t border-gray-100 bg-white">
          <div className="px-4 py-3 space-y-1">
            {NAV_LINKS.map(({ href, label, icon: Icon, desc }) => {
              const isActive = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setOpen(false)}
                  className={cn(
                    "flex items-center gap-3 rounded-xl px-3 py-3",
                    "transition-colors",
                    isActive
                      ? "bg-indigo-50 text-indigo-700"
                      : "text-gray-700 hover:bg-gray-50"
                  )}
                >
                  <div className={cn(
                    "flex h-8 w-8 items-center justify-center rounded-lg",
                    isActive ? "bg-indigo-100" : "bg-gray-100"
                  )}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{label}</p>
                    <p className="text-xs text-gray-400">{desc}</p>
                  </div>
                </Link>
              );
            })}
          </div>

          {/* Mobile auth */}
          <div className="border-t border-gray-100 px-4 py-3">
            <SignedOut>
              <div className="flex flex-col gap-2">
                <Link
                  href="/sign-in"
                  onClick={() => setOpen(false)}
                  className="rounded-xl border border-gray-200 px-4
                             py-2.5 text-center text-sm font-medium
                             text-gray-700 hover:bg-gray-50"
                >
                  Sign In
                </Link>
                <Link
                  href="/sign-up"
                  onClick={() => setOpen(false)}
                  className="rounded-xl bg-indigo-600 px-4 py-2.5
                             text-center text-sm font-semibold
                             text-white hover:bg-indigo-700"
                >
                  Get Started — Free
                </Link>
              </div>
            </SignedOut>
            <SignedIn>
              <div className="flex items-center gap-3">
                <UserButton />
                <p className="text-sm text-gray-600">My Account</p>
              </div>
            </SignedIn>
          </div>
        </div>
      )}
    </nav>
  );
}