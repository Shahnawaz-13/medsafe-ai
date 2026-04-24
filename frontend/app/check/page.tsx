// app/check/page.tsx
"use client";

import { useState, useRef } from "react";
import {
  Shield,
  Loader2,
  Download,
  RotateCcw,
  AlertCircle,
} from "lucide-react";
import DrugInputTag, { DrugTag } from "@/components/DrugInputTag";
import PersonalizeSection    from "@/components/PersonalizeSection";
import InteractionCard       from "@/components/InteractionCard";
import NoInteractionCard     from "@/components/NoInteractionCard";
import SummaryBanner         from "@/components/SummaryBanner";
import LoadingSkeleton       from "@/components/LoadingSkeleton";
import Disclaimer            from "@/components/Disclaimer";
import { analyzeInteractions } from "@/lib/api";
import { AnalysisResult }    from "@/types";
import { cn }                from "@/lib/utils";

type PageState = "idle" | "loading" | "results" | "error";

export default function CheckPage() {
  // ── State ───────────────────────────────────────────────────────
  const [drugs,    setDrugs]    = useState<DrugTag[]>([]);
  const [pageState, setPageState] = useState<PageState>("idle");
  const [result,   setResult]   = useState<AnalysisResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [personalize, setPersonalize] = useState<{
    age?:    number;
    gender?: string;
  }>({});

  const resultsRef = useRef<HTMLDivElement>(null);

  // ── Handlers ────────────────────────────────────────────────────
  const handleAddDrug = (drug: DrugTag) => {
    setDrugs((prev) => [...prev, drug]);
    // Clear error state when adding drugs
    if (pageState === "error") setPageState("idle");
  };

  const handleRemoveDrug = (id: string) => {
    setDrugs((prev) => prev.filter((d) => d.id !== id));
  };

  const handleClearAll = () => {
    setDrugs([]);
    setPageState("idle");
    setResult(null);
    setErrorMsg("");
  };

  const handleReset = () => {
    setDrugs([]);
    setPageState("idle");
    setResult(null);
    setErrorMsg("");
  };

  // ── Analyze ──────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    if (drugs.length < 2) return;

    setPageState("loading");
    setResult(null);
    setErrorMsg("");

    // Scroll to results on mobile
    setTimeout(() => {
      resultsRef.current?.scrollIntoView({
        behavior: "smooth",
        block:    "start",
      });
    }, 100);

    try {
      const response = await analyzeInteractions({
        drugs:  drugs.map((d) => d.displayName),
        age:    personalize.age,
        gender: personalize.gender,
      });

      setResult(response);
      setPageState("results");

      // Scroll to results after data loads
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({
          behavior: "smooth",
          block:    "start",
        });
      }, 200);

    } catch (err: unknown) {
      setErrorMsg(
        err instanceof Error
          ? err.message
          : "Something went wrong. Please try again."
      );
      setPageState("error");
    }
  };

  // ── PDF Download ─────────────────────────────────────────────────
  const handleDownloadPDF = async () => {
    if (!result) return;

    const { jsPDF } = await import("jspdf");
    const doc = new jsPDF();

    // Header
    doc.setFontSize(20);
    doc.setTextColor(55, 48, 163);
    doc.text("MedSafe AI", 20, 20);

    doc.setFontSize(12);
    doc.setTextColor(100, 100, 100);
    doc.text("Drug Interaction Safety Report", 20, 30);

    doc.setFontSize(10);
    doc.text(`Generated: ${new Date().toLocaleString("en-IN")}`, 20, 38);
    doc.text(`Check ID: ${result.checkId}`, 20, 46);

    // Drugs checked
    doc.setFontSize(12);
    doc.setTextColor(30, 30, 30);
    doc.text("Medications Checked:", 20, 58);

    doc.setFontSize(10);
    doc.setTextColor(80, 80, 80);
    const drugNames = drugs.map((d) => d.displayName).join(", ");
    const drugLines = doc.splitTextToSize(drugNames, 170);
    doc.text(drugLines, 20, 66);

    let y = 66 + drugLines.length * 7;

    // Overall severity
    doc.setFontSize(12);
    doc.setTextColor(30, 30, 30);
    doc.text(
      `Overall Risk: ${result.overallSeverity.toUpperCase()}`,
      20, y + 10
    );
    doc.setFontSize(10);
    doc.setTextColor(80, 80, 80);
    doc.text(result.summary, 20, y + 18);

    y += 28;

    // Interactions
    doc.setFontSize(12);
    doc.setTextColor(30, 30, 30);
    doc.text("Interaction Details:", 20, y + 10);
    y += 18;

    for (const pair of result.pairs) {
      if (y > 250) {
        doc.addPage();
        y = 20;
      }

      doc.setFontSize(11);
      doc.setTextColor(55, 48, 163);
      doc.text(
        `${pair.drug1} + ${pair.drug2} — ${pair.severity.toUpperCase()}`,
        20, y
      );
      y += 8;

      if (pair.plainExplanation) {
        doc.setFontSize(9);
        doc.setTextColor(80, 80, 80);
        const lines = doc.splitTextToSize(pair.plainExplanation, 170);
        doc.text(lines, 20, y);
        y += lines.length * 5 + 4;
      }

      if (pair.actionRequired) {
        doc.setFontSize(9);
        doc.setTextColor(150, 50, 50);
        doc.text(`Action: ${pair.actionRequired}`, 20, y);
        y += 7;
      }

      y += 4;
    }

    // Disclaimer
    if (y > 230) {
      doc.addPage();
      y = 20;
    }

    doc.setFontSize(8);
    doc.setTextColor(120, 120, 120);
    const discLines = doc.splitTextToSize(result.disclaimer, 170);
    doc.text(discLines, 20, y + 10);

    doc.save(`medsafe-report-${result.checkId.slice(0, 8)}.pdf`);
  };

  // ── Derived state ─────────────────────────────────────────────────
  const canAnalyze  = drugs.length >= 2 && pageState !== "loading";
  const hasResults  = pageState === "results" && result !== null;
  const isLoading   = pageState === "loading";

  // Split pairs into interactions and non-interactions
  const interactions = result?.pairs.filter(
    (p) => p.severity !== "none"
  ) || [];
  const cleanPairs = result?.pairs.filter(
    (p) => p.severity === "none"
  ) || [];

  // ── Render ────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">

        {/* ── Page header ─────────────────────────────────────── */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-10 w-10 items-center justify-center
                            rounded-xl bg-indigo-600">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
              Drug Interaction Checker
            </h1>
          </div>
          <p className="text-gray-500 ml-13">
            Enter your medications to check for interactions.
            Powered by OpenFDA + Groq AI.
          </p>
        </div>

        {/* ── Two-column layout ────────────────────────────────── */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">

          {/* ── LEFT PANEL — Input ─────────────────────────────── */}
          <div className="lg:col-span-2 space-y-4">
            <div className="rounded-2xl border border-gray-200
                            bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-gray-900 mb-1">
                Your Medications
              </h2>
              <p className="text-sm text-gray-500 mb-4">
                Type and select from suggestions, or press Enter to add.
              </p>

              {/* Drug input */}
              <DrugInputTag
                drugs={drugs}
                onAdd={handleAddDrug}
                onRemove={handleRemoveDrug}
                onClearAll={handleClearAll}
                disabled={isLoading}
              />

              {/* Personalise section */}
              <div className="mt-4">
                <PersonalizeSection
                  age={personalize.age}
                  gender={personalize.gender}
                  onChange={setPersonalize}
                />
              </div>

              {/* Analyze button */}
              <button
                onClick={handleAnalyze}
                disabled={!canAnalyze}
                title={
                  drugs.length < 2
                    ? "Add at least 2 medications"
                    : "Check interactions"
                }
                className={cn(
                  "mt-4 w-full rounded-xl py-3.5 px-6",
                  "text-base font-semibold transition-all duration-200",
                  "flex items-center justify-center gap-2",
                  canAnalyze
                    ? "bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm hover:shadow-md"
                    : "bg-gray-100 text-gray-400 cursor-not-allowed"
                )}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Analysing...
                  </>
                ) : (
                  <>
                    <Shield className="h-5 w-5" />
                    Check Interactions
                  </>
                )}
              </button>

              {/* Min drugs hint */}
              {drugs.length < 2 && (
                <p className="mt-2 text-center text-xs text-gray-400">
                  {drugs.length === 0
                    ? "Add 2 or more medications to get started"
                    : "Add 1 more medication to enable checking"
                  }
                </p>
              )}
            </div>

            {/* Quick reference */}
            <div className="rounded-2xl border border-gray-200
                            bg-white p-5 shadow-sm">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Severity Guide
              </h3>
              {[
                { emoji: "🚫", label: "Contraindicated",
                  desc:  "Never take together" },
                { emoji: "🔴", label: "High",
                  desc:  "Serious risk — see doctor" },
                { emoji: "🟡", label: "Moderate",
                  desc:  "Monitor closely" },
                { emoji: "🟢", label: "Low",
                  desc:  "Minor — mention to doctor" },
                { emoji: "⚪", label: "None",
                  desc:  "No known interaction" },
              ].map(({ emoji, label, desc }) => (
                <div key={label}
                  className="flex items-center gap-2 py-1.5">
                  <span className="text-lg w-6">{emoji}</span>
                  <div>
                    <span className="text-xs font-semibold
                                   text-gray-700">
                      {label}:
                    </span>
                    <span className="text-xs text-gray-500 ml-1">
                      {desc}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ── RIGHT PANEL — Results ──────────────────────────── */}
          <div ref={resultsRef} className="lg:col-span-3">

            {/* Idle state */}
            {pageState === "idle" && (
              <div className="flex h-full min-h-100 items-center
                              justify-center rounded-2xl border-2
                              border-dashed border-gray-200 bg-white">
                <div className="text-center px-8">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center
                                  justify-center rounded-2xl bg-indigo-50">
                    <Shield className="h-8 w-8 text-indigo-400" />
                  </div>
                  <h3 className="text-base font-semibold text-gray-700 mb-2">
                    Your results will appear here
                  </h3>
                  <p className="text-sm text-gray-400 max-w-xs mx-auto">
                    Add at least 2 medications and click
                    &quot;Check Interactions&quot; to get your
                    AI-powered safety report.
                  </p>
                </div>
              </div>
            )}

            {/* Loading state */}
            {isLoading && (
              <div className="space-y-4">
                <div className="rounded-2xl border border-gray-200
                                bg-white p-6 shadow-sm">
                  <div className="flex items-center gap-3 mb-4">
                    <Loader2 className="h-5 w-5 animate-spin
                                       text-indigo-500" />
                    <p className="text-sm font-medium text-gray-600">
                      Analysing {drugs.length} medications
                      across {drugs.length * (drugs.length - 1) / 2} pairs...
                    </p>
                  </div>
                  <div className="space-y-2">
                    {[
                      "Normalising drug names via RxNorm...",
                      "Checking OpenFDA drug interaction database...",
                      "Generating AI explanations via Groq...",
                    ].map((step, i) => (
                      <div key={i}
                        className="flex items-center gap-2 text-xs
                                   text-gray-400">
                        <div className="h-1.5 w-1.5 rounded-full
                                        bg-indigo-300 animate-pulse" />
                        {step}
                      </div>
                    ))}
                  </div>
                </div>
                <LoadingSkeleton count={3} />
              </div>
            )}

            {/* Error state */}
            {pageState === "error" && (
              <div className="rounded-2xl border border-red-200
                              bg-red-50 p-6 shadow-sm">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-red-500
                                         shrink-0 mt-0.5" />
                  <div>
                    <h3 className="text-sm font-semibold text-red-800 mb-1">
                      Analysis Failed
                    </h3>
                    <p className="text-sm text-red-700">{errorMsg}</p>
                    <button
                      onClick={handleAnalyze}
                      className="mt-3 text-sm font-medium text-red-600
                                 hover:text-red-800 underline"
                    >
                      Try again
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Results state */}
            {hasResults && result && (
              <div className="space-y-4">
                {/* Action buttons */}
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <p className="text-sm text-gray-500">
                    Report generated in {result.responseTimeMs}ms
                    {result.cachedPairs > 0 &&
                      ` · ${result.cachedPairs} from cache`
                    }
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={handleDownloadPDF}
                      className="flex items-center gap-1.5 rounded-lg
                                 border border-gray-200 bg-white px-3
                                 py-2 text-xs font-medium text-gray-600
                                 hover:bg-gray-50 transition-colors"
                    >
                      <Download className="h-3.5 w-3.5" />
                      Download PDF
                    </button>
                    <button
                      onClick={handleReset}
                      className="flex items-center gap-1.5 rounded-lg
                                 border border-gray-200 bg-white px-3
                                 py-2 text-xs font-medium text-gray-600
                                 hover:bg-gray-50 transition-colors"
                    >
                      <RotateCcw className="h-3.5 w-3.5" />
                      New Check
                    </button>
                  </div>
                </div>

                {/* Summary banner */}
                <SummaryBanner
                  overallSeverity={result.overallSeverity}
                  summary={result.summary}
                  interactionCount={result.interactionsFound}
                  totalPairs={result.pairsChecked}
                  drugsCount={result.drugsSubmitted}
                />

                {/* Drug identification info */}
                {result.drugsIdentified < result.drugsSubmitted && (
                  <div className="rounded-xl border border-amber-200
                                  bg-amber-50 p-4">
                    <p className="text-xs text-amber-700">
                      <span className="font-semibold">Note:</span>
                      {" "}
                      {result.drugsSubmitted - result.drugsIdentified} of{" "}
                      {result.drugsSubmitted} drug names could not be
                      verified in RxNorm. Results may be incomplete.
                      Check spelling or use generic names.
                    </p>
                  </div>
                )}

                {/* Interaction cards */}
                {interactions.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-600
                                   uppercase tracking-wide mb-3">
                      Interactions Found ({interactions.length})
                    </h3>
                    <div className="space-y-3">
                      {interactions.map((pair, idx) => (
                        <InteractionCard
                          key={`${pair.drug1}-${pair.drug2}`}
                          pair={pair}
                          index={idx}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* No interaction pairs */}
                {cleanPairs.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-400
                                   uppercase tracking-wide mb-2">
                      No Interaction Detected ({cleanPairs.length})
                    </h3>
                    <div className="space-y-2">
                      {cleanPairs.map((pair) => (
                        <NoInteractionCard
                          key={`${pair.drug1}-${pair.drug2}`}
                          drug1={pair.drug1}
                          drug2={pair.drug2}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Fallback notice */}
                {result.isFallback && (
                  <div className="rounded-xl border border-blue-200
                                  bg-blue-50 p-4">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="h-4 w-4 text-blue-500
                                             shrink-0 mt-0.5" />
                      <p className="text-xs text-blue-700">
                        <span className="font-semibold">Note:</span>
                        {" "}AI explanation service was temporarily
                        unavailable. Severity shown is based on
                        pre-classified medical data. Please consult
                        your pharmacist for full details.
                      </p>
                    </div>
                  </div>
                )}

                {/* Disclaimer */}
                <Disclaimer />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

