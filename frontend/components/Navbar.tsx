// components/Navbar.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, X, Shield } from "lucide-react";
import {
  UserButton,
  useAuth,
} from "@clerk/nextjs";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "/check",   label: "Check Drugs" },
  { href: "/chat",    label: "RxChat"      },
  { href: "/history", label: "History"     },
  { href: "/upload",  label: "Upload Rx"   },
];

export default function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const { isSignedIn } = useAuth();

  return (
    <nav className="sticky top-0 z-50 w-full border-b
                    border-gray-100 bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center
                      justify-between px-4 sm:px-6 lg:px-8">

        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center
                          rounded-xl bg-indigo-600">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold text-indigo-700">
            MedSafe
            <span className="text-teal-600">AI</span>
          </span>
        </Link>

        {/* Desktop nav links */}
        <div className="hidden items-center gap-1 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
                pathname === link.href
                  ? "bg-indigo-50 text-indigo-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Desktop auth buttons */}
        <div className="hidden items-center gap-3 md:flex">
          {!isSignedIn ? (
            <>
              <Link
                href="/sign-in"
                className="text-sm font-medium text-gray-600
                           hover:text-gray-900"
              >
                Sign In
              </Link>
              <Link
                href="/sign-up"
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm
                           font-medium text-white hover:bg-indigo-700
                           transition-colors"
              >
                Get Started
              </Link>
            </>
          ) : (
            <UserButton />
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden rounded-lg p-2 text-gray-600
                     hover:bg-gray-100"
          onClick={() => setOpen(!open)}
        >
          {open
            ? <X className="h-5 w-5" />
            : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="border-t border-gray-100 bg-white px-4
                        py-3 md:hidden">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className={cn(
                "block rounded-lg px-4 py-2.5 text-sm font-medium",
                pathname === link.href
                  ? "bg-indigo-50 text-indigo-700"
                  : "text-gray-700 hover:bg-gray-50"
              )}
            >
              {link.label}
            </Link>
          ))}

          <div className="mt-3 border-t border-gray-100 pt-3">
            {!isSignedIn ? (
              <>
                <Link
                  href="/sign-in"
                  className="block rounded-lg px-4 py-2.5 text-sm
                             font-medium text-gray-700 hover:bg-gray-50"
                >
                  Sign In
                </Link>
                <Link
                  href="/sign-up"
                  className="mt-1 block rounded-lg bg-indigo-600 px-4
                             py-2.5 text-center text-sm font-medium
                             text-white"
                >
                  Get Started
                </Link>
              </>
            ) : (
              <UserButton />
            )}
          </div>
        </div>
      )}
    </nav>
  );
}