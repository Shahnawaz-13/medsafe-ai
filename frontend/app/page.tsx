// app/page.tsx
import Link from "next/link";
import {
  Shield,
  Brain,
  Database,
  ArrowRight,
  Zap,
  Lock,
  Users,
} from "lucide-react";

// ── Static data ───────────────────────────────────────────────────────
const FEATURES = [
  {
    icon:  Shield,
    title: "Severity-Coded Warnings",
    desc:  "Every drug pair is classified as Contraindicated, High, Moderate, Low, or None — colour-coded for instant understanding.",
    color: "bg-indigo-50 text-indigo-600",
  },
  {
    icon:  Brain,
    title: "AI Plain-Language Explanations",
    desc:  "Groq LLaMA AI rewrites complex pharmacology into simple language anyone can understand — no medical degree required.",
    color: "bg-purple-50 text-purple-600",
  },
  {
    icon:  Database,
    title: "Trusted Medical Databases",
    desc:  "All interaction data sourced from OpenFDA and RxNorm — US government-maintained, updated regularly.",
    color: "bg-teal-50 text-teal-600",
  },
  {
    icon:  Zap,
    title: "Results in Seconds",
    desc:  "Our caching layer serves repeat queries instantly. New drug combinations resolved in under 8 seconds.",
    color: "bg-amber-50 text-amber-600",
  },
  {
    icon:  Lock,
    title: "Privacy First",
    desc:  "Anonymous by default. No drug data stored without your consent. No ads. No data selling. Ever.",
    color: "bg-green-50 text-green-600",
  },
  {
    icon:  Users,
    title: "Built for Everyone",
    desc:  "Patients, caregivers, pharmacists, and medical students all benefit from instant drug safety intelligence.",
    color: "bg-rose-50 text-rose-600",
  },
];

const STATS = [
  { value: "125K+", label: "Preventable deaths/year from ADEs" },
  { value: "42B",   label: "USD lost to medication errors annually" },
  { value: "50%",   label: "Risk with 5+ concurrent medications" },
  { value: "Free",  label: "Always free for patients" },
];

const HOW_IT_WORKS = [
  {
    step:  "1",
    title: "Enter Your Medications",
    desc:  "Type your drug names one by one. Our autocomplete suggests canonical names from RxNorm as you type.",
  },
  {
    step:  "2",
    title: "AI Analyses All Pairs",
    desc:  "We check every possible drug pair against OpenFDA data and classify severity using a keyword-based medical engine.",
  },
  {
    step:  "3",
    title: "Read Your Safety Report",
    desc:  "Get plain-English explanations, watch-for warnings, action steps, and safer alternatives — all in one clear report.",
  },
];

const SEVERITY_EXAMPLES = [
  {
    emoji:  "🚫",
    label:  "CONTRAINDICATED",
    drugs:  "Sildenafil + Nitroglycerin",
    text:   "Never take together. Life-threatening blood pressure drop.",
    bg:     "bg-red-50 border-red-200",
    text_c: "text-red-800",
  },
  {
    emoji:  "🔴",
    label:  "HIGH",
    drugs:  "Warfarin + Aspirin",
    text:   "Serious bleeding risk. Consult your doctor immediately.",
    bg:     "bg-orange-50 border-orange-200",
    text_c: "text-orange-800",
  },
  {
    emoji:  "🟡",
    label:  "MODERATE",
    drugs:  "Lisinopril + Aspirin",
    text:   "May reduce effectiveness. Monitor blood pressure closely.",
    bg:     "bg-yellow-50 border-yellow-200",
    text_c: "text-yellow-800",
  },
];

// ── Page ──────────────────────────────────────────────────────────────
export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">

      {/* ── HERO ──────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-gradient-to-br
                          from-indigo-950 via-indigo-900 to-indigo-800">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `radial-gradient(circle at 2px 2px,
              white 1px, transparent 0)`,
            backgroundSize: "40px 40px",
          }}
        />

        <div className="relative mx-auto max-w-6xl px-4 py-20
                        sm:px-6 lg:px-8 lg:py-28">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 rounded-full
                            border border-indigo-500/30 bg-indigo-500/10
                            px-4 py-1.5 mb-6">
              <Shield className="h-4 w-4 text-indigo-300" />
              <span className="text-sm text-indigo-300 font-medium">
                Powered by OpenFDA + Groq AI
              </span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl font-bold tracking-tight text-white
                           sm:text-5xl lg:text-6xl">
              Check Your Medications
              <span className="block text-indigo-300 mt-1">
                for Safety
              </span>
            </h1>

            {/* Subheadline */}
            <p className="mt-6 text-lg text-indigo-200 max-w-2xl
                          mx-auto leading-relaxed">
              Enter your medication list and get instant AI-powered
              interaction warnings — severity-coded, plain-language,
              and completely free. No login required.
            </p>

            {/* CTA buttons */}
            <div className="mt-8 flex flex-col sm:flex-row gap-3
                            justify-center">
              <Link
                href="/check"
                className="inline-flex items-center gap-2 rounded-xl
                           bg-white px-6 py-3.5 text-base font-semibold
                           text-indigo-700 shadow-lg hover:bg-indigo-50
                           transition-all duration-200 hover:shadow-xl"
              >
                <Shield className="h-5 w-5" />
                Check Interactions Now
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/chat"
                className="inline-flex items-center gap-2 rounded-xl
                           border border-indigo-400/40 bg-indigo-500/10
                           px-6 py-3.5 text-base font-semibold
                           text-indigo-200 hover:bg-indigo-500/20
                           transition-all duration-200"
              >
                <Brain className="h-5 w-5" />
                Ask RxChat
              </Link>
            </div>

            {/* Trust badges */}
            <div className="mt-8 flex flex-wrap gap-4 justify-center">
              {[
                "✓ 100% Free",
                "✓ No Login Required",
                "✓ FDA-sourced Data",
                "✓ No Data Sold",
              ].map((badge) => (
                <span key={badge}
                  className="text-sm text-indigo-300 font-medium">
                  {badge}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── STATS ─────────────────────────────────────────────────── */}
      <section className="border-b border-gray-100 bg-gray-50 py-12">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
            {STATS.map(({ value, label }) => (
              <div key={label} className="text-center">
                <p className="text-3xl font-bold text-indigo-700">
                  {value}
                </p>
                <p className="mt-1 text-sm text-gray-500">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── SEVERITY PREVIEW ──────────────────────────────────────── */}
      <section className="py-16 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
              See What You&apos;ll Get
            </h2>
            <p className="mt-3 text-gray-500 max-w-xl mx-auto">
              Real interaction examples from our AI safety engine
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {SEVERITY_EXAMPLES.map(
              ({ emoji, label, drugs, text, bg, text_c }) => (
                <div
                  key={label}
                  className={`rounded-xl border-2 p-5 ${bg}`}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-2xl">{emoji}</span>
                    <span className={`text-xs font-bold
                                    tracking-wide ${text_c}`}>
                      {label}
                    </span>
                  </div>
                  <p className={`text-sm font-semibold mb-1 ${text_c}`}>
                    {drugs}
                  </p>
                  <p className={`text-sm ${text_c} opacity-80`}>
                    {text}
                  </p>
                </div>
              )
            )}
          </div>

          <div className="mt-6 text-center">
            <Link
              href="/check"
              className="inline-flex items-center gap-2 text-sm
                         font-semibold text-indigo-600
                         hover:text-indigo-800"
            >
              Check your own medications
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ──────────────────────────────────────────── */}
      <section className="py-16 bg-gray-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
              How It Works
            </h2>
            <p className="mt-3 text-gray-500">
              Three steps to your drug safety report
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-3">
            {HOW_IT_WORKS.map(({ step, title, desc }) => (
              <div key={step}
                className="relative rounded-2xl bg-white border
                           border-gray-200 p-6 shadow-sm">
                {/* Step number */}
                <div className="mb-4 flex h-10 w-10 items-center
                                justify-center rounded-xl bg-indigo-600">
                  <span className="text-base font-bold text-white">
                    {step}
                  </span>
                </div>

                {/* Arrow connector (hidden on mobile) */}
                {step !== "3" && (
                  <ArrowRight
                    className="absolute -right-3 top-8 hidden h-5 w-5
                               text-gray-300 sm:block z-10"
                  />
                )}

                <h3 className="text-base font-semibold text-gray-900 mb-2">
                  {title}
                </h3>
                <p className="text-sm text-gray-500 leading-relaxed">
                  {desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FEATURES ──────────────────────────────────────────────── */}
      <section className="py-16 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
              Everything You Need
            </h2>
            <p className="mt-3 text-gray-500 max-w-xl mx-auto">
              Built with medical accuracy and patient safety
              as the top priorities
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map(({ icon: Icon, title, desc, color }) => (
              <div
                key={title}
                className="rounded-2xl border border-gray-100 bg-white
                           p-6 shadow-sm hover:shadow-md
                           transition-shadow duration-200"
              >
                <div className={`mb-4 inline-flex h-10 w-10 items-center
                                justify-center rounded-xl ${color}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="text-base font-semibold text-gray-900 mb-2">
                  {title}
                </h3>
                <p className="text-sm text-gray-500 leading-relaxed">
                  {desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── WHO IS IT FOR ─────────────────────────────────────────── */}
      <section className="py-16 bg-indigo-950">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">
              Who Uses MedSafe AI?
            </h2>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                icon:  "💊",
                title: "Patients",
                desc:  "Check your daily medications before taking them together",
              },
              {
                icon:  "👨‍👩‍👧",
                title: "Caregivers",
                desc:  "Manage elderly parent's complex medication schedules safely",
              },
              {
                icon:  "⚕️",
                title: "Pharmacists",
                desc:  "Quick cross-check at the dispensing counter",
              },
              {
                icon:  "🎓",
                title: "Medical Students",
                desc:  "Learn drug interactions with real clinical examples",
              },
            ].map(({ icon, title, desc }) => (
              <div key={title}
                className="rounded-xl border border-indigo-800
                           bg-indigo-900/50 p-5 text-center">
                <span className="text-3xl mb-3 block">{icon}</span>
                <h3 className="text-sm font-semibold text-white mb-1">
                  {title}
                </h3>
                <p className="text-xs text-indigo-300 leading-relaxed">
                  {desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FINAL CTA ─────────────────────────────────────────────── */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-2xl px-4 text-center">
          <Shield className="mx-auto h-12 w-12 text-indigo-500 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl mb-4">
            Start Checking Your Medications
          </h2>
          <p className="text-gray-500 mb-8 leading-relaxed">
            Free, instant, and powered by trusted medical databases.
            No account needed. No credit card. No catch.
          </p>
          <Link
            href="/check"
            className="inline-flex items-center gap-2 rounded-xl
                       bg-indigo-600 px-8 py-4 text-base font-semibold
                       text-white shadow-lg hover:bg-indigo-700
                       transition-all duration-200 hover:shadow-xl"
          >
            <Shield className="h-5 w-5" />
            Check Interactions — Free
            <ArrowRight className="h-4 w-4" />
          </Link>

          {/* Disclaimer */}
          <p className="mt-6 text-xs text-gray-400 max-w-md mx-auto">
            MedSafe AI is for educational purposes only and does not
            constitute medical advice. Always consult a licensed
            physician or pharmacist before making medication decisions.
          </p>
        </div>
      </section>
    </div>
  );
}