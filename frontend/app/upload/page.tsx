// app/upload/page.tsx
"use client";

import {
  useState,
  useRef,
  useCallback,
  DragEvent,
  ChangeEvent,
} from "react";
import { useRouter }  from "next/navigation";
import {
  Upload,
  FileImage,
  X,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ArrowRight,
  Shield,
  Eye,
} from "lucide-react";
import Disclaimer from "@/components/Disclaimer";
import { cn }     from "@/lib/utils";

type UploadState =
  | "idle"
  | "dragging"
  | "preview"
  | "extracting"
  | "extracted"
  | "error";

interface ExtractedDrug {
  name:     string;
  selected: boolean;
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function UploadPage() {
  const router = useRouter();

  const [uploadState,     setUploadState]     = useState<UploadState>("idle");
  const [selectedFile,    setSelectedFile]    = useState<File | null>(null);
  const [previewUrl,      setPreviewUrl]      = useState<string | null>(null);
  const [extractedDrugs,  setExtractedDrugs]  = useState<ExtractedDrug[]>([]);
  const [confidence,      setConfidence]      = useState(0);
  const [errorMsg,        setErrorMsg]        = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── File validation ───────────────────────────────────────────────
  const validateFile = (file: File): string | null => {
    const allowed = ["image/jpeg", "image/png", "application/pdf"];
    if (!allowed.includes(file.type)) {
      return "Only JPG, PNG, and PDF files are supported.";
    }
    if (file.size > 5 * 1024 * 1024) {
      return "File size must be under 5MB.";
    }
    return null;
  };

  // ── Handle file selection ─────────────────────────────────────────
  const handleFile = useCallback((file: File) => {
    const err = validateFile(file);
    if (err) {
      setErrorMsg(err);
      setUploadState("error");
      return;
    }

    setSelectedFile(file);
    setErrorMsg("");

    // Create preview URL for images
    if (file.type.startsWith("image/")) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }

    setUploadState("preview");
  }, []);

  // ── Drag handlers ─────────────────────────────────────────────────
  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setUploadState("dragging");
  };

  const handleDragLeave = () => {
    if (uploadState === "dragging") setUploadState("idle");
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  // ── Extract drugs via OCR ─────────────────────────────────────────
  const handleExtract = async () => {
    if (!selectedFile) return;

    setUploadState("extracting");
    setExtractedDrugs([]);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const res = await fetch(
        `${API_URL}/api/upload-prescription`,
        { method: "POST", body: formData }
      );

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        
        const errorMessage =
          typeof body === "object" && body !== null && "detail" in body
            ? (body as { detail?: { message?: string } }).detail?.message
            : undefined;

        throw new Error(
          errorMessage || "Extraction failed. Please try a clearer image."
        );
      }

      const data: unknown = await res.json();

      const dataObj = 
        typeof data === "object" && data !== null
          ? (data as { 
              extracted_drugs?: unknown;
              confidence?: unknown;
            })
          : {};

      const drugs= Array.isArray(dataObj.extracted_drugs)
            ? dataObj.extracted_drugs.filter(
                (drug): drug is string => typeof drug === "string" 
              )
            : [];
      if (drugs.length === 0) {
        throw new Error(
          "No drug names could be extracted. " +
          "Try a clearer, printed prescription."
        );
      }

      setExtractedDrugs(
        drugs.map((name) => ({ name, selected: true }))
      );

      setConfidence(
        typeof dataObj.confidence === "number"
          ? dataObj.confidence
          : 0
      );
      setUploadState("extracted");

    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : "Extraction failed. Please try again.";
        setErrorMsg(message);
        setUploadState("error");
    }
  };

  // ── Toggle drug selection ─────────────────────────────────────────
  const toggleDrug = (idx: number) => {
    setExtractedDrugs((prev) =>
      prev.map((d, i) =>
        i === idx ? { ...d, selected: !d.selected } : d
      )
    );
  };

  // ── Check selected drugs ──────────────────────────────────────────
  const handleCheckSelected = () => {
    const selected = extractedDrugs
      .filter((d) => d.selected)
      .map((d) => d.name);

    if (selected.length < 2) {
      alert("Please select at least 2 drugs to check.");
      return;
    }

    const params = new URLSearchParams();
    params.set("drugs", selected.join(","));
    router.push(`/check?drugs=${encodeURIComponent(selected.join(","))}`);
  };

  // ── Reset ─────────────────────────────────────────────────────────
  const handleReset = () => {
    setUploadState("idle");
    setSelectedFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setExtractedDrugs([]);
    setErrorMsg("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const selectedCount = extractedDrugs.filter((d) => d.selected).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">

        {/* ── Header ──────────────────────────────────────────────── */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-10 w-10 items-center justify-center
                            rounded-xl bg-indigo-600">
              <Upload className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">
              Upload Prescription
            </h1>
          </div>
          <p className="text-gray-500 text-sm">
            Upload a prescription photo and we&apos;ll extract
            drug names automatically using OCR.
          </p>
        </div>

        {/* ── Drop zone ──────────────────────────────────────────── */}
        {(uploadState === "idle" || uploadState === "dragging") && (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={cn(
              "relative flex flex-col items-center justify-center",
              "rounded-2xl border-2 border-dashed p-12 cursor-pointer",
              "transition-all duration-200",
              uploadState === "dragging"
                ? "border-indigo-400 bg-indigo-50 scale-[1.01]"
                : "border-gray-300 bg-white hover:border-indigo-300 hover:bg-indigo-50/30"
            )}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,application/pdf"
              onChange={handleFileInput}
              className="hidden"
              aria-label="Upload prescription file"
            />

            <div className={cn(
              "mb-4 flex h-16 w-16 items-center justify-center rounded-2xl",
              uploadState === "dragging"
                ? "bg-indigo-100"
                : "bg-gray-100"
            )}>
              <FileImage className={cn(
                "h-8 w-8",
                uploadState === "dragging"
                  ? "text-indigo-500"
                  : "text-gray-400"
              )} />
            </div>

            <p className="text-base font-semibold text-gray-700 mb-1">
              {uploadState === "dragging"
                ? "Drop your prescription here"
                : "Drag your prescription here"
              }
            </p>
            <p className="text-sm text-gray-400 mb-4">
              or{" "}
              <span className="text-indigo-600 font-medium
                              hover:text-indigo-800">
                browse files
              </span>
            </p>

            <div className="flex gap-3 text-xs text-gray-400">
              <span className="rounded-full border border-gray-200
                               px-2.5 py-1">
                JPG
              </span>
              <span className="rounded-full border border-gray-200
                               px-2.5 py-1">
                PNG
              </span>
              <span className="rounded-full border border-gray-200
                               px-2.5 py-1">
                PDF
              </span>
              <span className="rounded-full border border-gray-200
                               px-2.5 py-1">
                Max 5MB
              </span>
            </div>
          </div>
        )}

        {/* ── Preview state ─────────────────────────────────────── */}
        {uploadState === "preview" && selectedFile && (
          <div className="rounded-2xl border border-gray-200 bg-white
                          p-6 shadow-sm">
            <div className="flex items-start gap-4 mb-5">
              {/* Image preview */}
              {previewUrl ? (
                <div className="relative h-24 w-24 shrink-0 rounded-xl
                                overflow-hidden border border-gray-200">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={previewUrl}
                    alt="Prescription preview"
                    className="h-full w-full object-cover"
                  />
                  <button
                    type="button"
                    aria-label="Remove selected file"
                    onClick={handleReset}
                    className="absolute top-1 right-1 h-5 w-5 rounded-full
                               bg-black/50 flex items-center justify-center"
                  >
                    <X className="h-3 w-3 text-white" />
                  </button>
                </div>
              ) : (
                <div className="flex h-24 w-24 shrink-0 items-center
                                justify-center rounded-xl bg-gray-100">
                  <FileImage className="h-10 w-10 text-gray-400" />
                </div>
              )}

              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 mb-1
                              truncate">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-gray-500 mb-3">
                  {(selectedFile.size / 1024).toFixed(1)} KB ·
                  {" "}{selectedFile.type.split("/")[1].toUpperCase()}
                </p>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <p className="text-xs text-green-700 font-medium">
                    File ready for extraction
                  </p>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleExtract}
                className="flex-1 flex items-center justify-center gap-2
                           rounded-xl bg-indigo-600 py-3 text-sm
                           font-semibold text-white hover:bg-indigo-700
                           transition-colors"
              >
                <Eye className="h-4 w-4" />
                Extract Drug Names
              </button>
              <button
                onClick={handleReset}
                className="rounded-xl border border-gray-200 px-4 py-3
                           text-sm font-medium text-gray-600
                           hover:bg-gray-50 transition-colors"
              >
                Change
              </button>
            </div>
          </div>
        )}

        {/* ── Extracting state ─────────────────────────────────── */}
        {uploadState === "extracting" && (
          <div className="rounded-2xl border border-indigo-200 bg-white
                          p-8 shadow-sm text-center">
            <Loader2 className="h-10 w-10 animate-spin text-indigo-500
                               mx-auto mb-4" />
            <h3 className="text-base font-semibold text-gray-900 mb-2">
              Reading your prescription...
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Our OCR engine is extracting drug names from your image.
            </p>
            <div className="space-y-2 text-left max-w-xs mx-auto">
              {[
                "Processing image...",
                "Running OCR text extraction...",
                "Matching drug names with RxNorm...",
              ].map((step, i) => (
                <div key={i}
                  className="flex items-center gap-2 text-xs text-gray-400">
                  <div className="h-1.5 w-1.5 rounded-full bg-indigo-300
                                  animate-pulse" />
                  {step}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Extracted state ──────────────────────────────────── */}
        {uploadState === "extracted" && extractedDrugs.length > 0 && (
          <div className="rounded-2xl border border-gray-200 bg-white
                          p-6 shadow-sm">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-semibold text-gray-900 mb-1">
                  Extracted Drug Names
                </h3>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <p className="text-xs text-green-700">
                    {extractedDrugs.length} drugs found
                    {confidence > 0 &&
                      ` · ${Math.round(confidence * 100)}% confidence`
                    }
                  </p>
                </div>
              </div>
              <button
                onClick={handleReset}
                className="text-xs text-gray-400 hover:text-gray-600
                           underline"
              >
                Upload different file
              </button>
            </div>

            {/* Drug selection */}
            <p className="text-xs text-gray-500 mb-3">
              Select the drugs to include in your interaction check:
            </p>
            <div className="space-y-2 mb-5">
              {extractedDrugs.map((drug, idx) => (
                <button
                  key={idx}
                  onClick={() => toggleDrug(idx)}
                  className={cn(
                    "flex w-full items-center gap-3 rounded-xl",
                    "border px-4 py-3 text-left transition-colors",
                    drug.selected
                      ? "border-indigo-300 bg-indigo-50"
                      : "border-gray-200 bg-gray-50"
                  )}
                >
                  <div className={cn(
                    "h-5 w-5 shrink-0 rounded-md border-2 flex items-center",
                    "justify-center transition-colors",
                    drug.selected
                      ? "border-indigo-500 bg-indigo-500"
                      : "border-gray-300 bg-white"
                  )}>
                    {drug.selected && (
                      <CheckCircle2 className="h-3.5 w-3.5 text-white" />
                    )}
                  </div>
                  <span className={cn(
                    "text-sm font-medium",
                    drug.selected ? "text-indigo-800" : "text-gray-600"
                  )}>
                    {drug.name}
                  </span>
                </button>
              ))}
            </div>

            {/* Note */}
            <div className="rounded-lg bg-amber-50 border border-amber-200
                            p-3 mb-4">
              <p className="text-xs text-amber-700">
                <span className="font-semibold">Note:</span>
                {" "}Please verify the extracted names before checking.
                OCR works best with printed prescriptions.
                Handwritten text may have lower accuracy.
              </p>
            </div>

            {/* CTA */}
            <button
              onClick={handleCheckSelected}
              disabled={selectedCount < 2}
              className={cn(
                "w-full flex items-center justify-center gap-2",
                "rounded-xl py-3.5 text-sm font-semibold transition-colors",
                selectedCount >= 2
                  ? "bg-indigo-600 text-white hover:bg-indigo-700"
                  : "bg-gray-100 text-gray-400 cursor-not-allowed"
              )}
            >
              <Shield className="h-4 w-4" />
              Check {selectedCount} Drug
              {selectedCount !== 1 ? "s" : ""} for Interactions
              <ArrowRight className="h-4 w-4" />
            </button>

            {selectedCount < 2 && (
              <p className="mt-2 text-center text-xs text-gray-400">
                Select at least 2 drugs to check interactions
              </p>
            )}
          </div>
        )}

        {/* ── Error state ──────────────────────────────────────── */}
        {uploadState === "error" && (
          <div className="rounded-2xl border border-red-200 bg-red-50
                          p-6 text-center shadow-sm">
            <AlertCircle className="h-10 w-10 text-red-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-red-800 mb-2">
              Extraction Failed
            </h3>
            <p className="text-sm text-red-700 mb-4">{errorMsg}</p>
            <button
              onClick={handleReset}
              className="rounded-xl bg-red-600 px-5 py-2.5 text-sm
                         font-semibold text-white hover:bg-red-700
                         transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* ── Tips ─────────────────────────────────────────────── */}
        {(uploadState === "idle" || uploadState === "dragging") && (
          <div className="mt-6 rounded-xl border border-gray-200
                          bg-white p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              Tips for Best Results
            </h3>
            <div className="space-y-2">
              {[
                "Use printed prescriptions — handwriting is harder to read",
                "Ensure good lighting and a flat surface when photographing",
                "Make sure all drug names are clearly visible",
                "PDF prescriptions from online pharmacies work best",
              ].map((tip) => (
                <div key={tip} className="flex gap-2 text-xs text-gray-500">
                  <CheckCircle2 className="h-3.5 w-3.5 mt-0.5 shrink-0
                                          text-green-500" />
                  {tip}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Disclaimer ───────────────────────────────────────── */}
        <div className="mt-6">
          <Disclaimer compact />
        </div>
      </div>
    </div>
  );
} 
