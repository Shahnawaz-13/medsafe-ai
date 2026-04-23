// components/LoadingSkeleton.tsx

// ── Single skeleton card ──────────────────────────────────────────────
function SkeletonCard() {
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-5">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="space-y-2">
          <div className="h-3 w-20 animate-pulse rounded-full bg-gray-100" />
          <div className="h-5 w-48 animate-pulse rounded-full bg-gray-200" />
        </div>
        <div className="h-7 w-28 animate-pulse rounded-full bg-gray-200" />
      </div>

      {/* Body lines */}
      <div className="space-y-2">
        <div className="h-4 w-full  animate-pulse rounded bg-gray-100" />
        <div className="h-4 w-5/6   animate-pulse rounded bg-gray-100" />
        <div className="h-4 w-4/6   animate-pulse rounded bg-gray-100" />
      </div>

      {/* Watch-for box */}
      <div className="mt-4 rounded-lg bg-yellow-50 p-3">
        <div className="h-3 w-32 animate-pulse rounded bg-yellow-200 mb-2" />
        <div className="h-3 w-full animate-pulse rounded bg-yellow-100" />
      </div>

      {/* Footer */}
      <div className="mt-4 flex gap-2">
        <div className="h-8 w-32 animate-pulse rounded-lg bg-gray-100" />
        <div className="h-8 w-24 animate-pulse rounded-lg bg-gray-100" />
      </div>
    </div>
  );
}

// ── Summary banner skeleton ───────────────────────────────────────────
function SkeletonBanner() {
  return (
    <div className="rounded-xl bg-gray-100 p-4 animate-pulse mb-4">
      <div className="h-5 w-56 bg-gray-200 rounded-full mb-2" />
      <div className="h-4 w-72 bg-gray-200 rounded-full" />
    </div>
  );
}

interface Props {
  count?: number;
}

export default function LoadingSkeleton({ count = 3 }: Props) {
  return (
    <div className="space-y-4">
      <SkeletonBanner />
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}