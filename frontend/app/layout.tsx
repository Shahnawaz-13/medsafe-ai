// app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import Navbar from "@/components/Navbar";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MedSafe AI — Drug Interaction Checker",
  description:
    "AI-powered drug interaction checker. Enter your " +
    "medications and get instant safety warnings powered " +
    "by trusted medical databases and Claude AI.",
  keywords: ["drug interaction", "medication safety", "AI health"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ClerkProvider>
          <Navbar />

          <main className="min-h-screen bg-gray-50">
            {children}
          </main>

          <footer className="border-t border-gray-100 bg-white
                             py-6 text-center text-xs text-gray-400">
            MedSafe AI is for informational purposes only.
            Not a substitute for professional medical advice.
            © 2026 MedSafe AI
          </footer>
        </ClerkProvider>
      </body>
    </html>
  );
}