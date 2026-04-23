# test_day9_benchmark.py (delete after)
import asyncio
import time
from dotenv import load_dotenv
load_dotenv()

from app.database import connect_db, close_db
from app.services.normaliser import normalize_drug_list
from app.services.pair_generator import generate_pairs
from app.services.interaction_resolver import resolve_all_pairs
from app.services.alternative_service import get_alternatives_for_pairs
from app.services.cache_service import (
    get_cache_stats,
    clear_all_cache,
)
from app.services.severity_classifier import (
    get_severity_emoji,
    get_overall_severity,
)


async def benchmark():
    print("=" * 65)
    print("Day 9 — Full Pipeline Benchmark")
    print("=" * 65)

    await connect_db()

    # Clear cache for clean benchmark
    cleared = await clear_all_cache()
    print(f"\n[0] Cache cleared: {cleared} documents removed")

    # Test with 5 drugs = 10 pairs
    test_drugs = [
        "Warfarin",
        "Aspirin",
        "Metformin",
        "Lisinopril",
        "Atorvastatin",
    ]

    print(f"\n[1] Normalising {len(test_drugs)} drugs...")
    t0         = time.time()
    normalized = await normalize_drug_list(test_drugs)
    t1         = time.time()

    for r in normalized:
        status = "✅" if r["found"] else "❌"
        print(
            f"   {status} {r['input_name']:15} → "
            f"{r['normalized_name']:15} | "
            f"RxCUI: {r['rxcui']}"
        )
    print(f"   Time: {(t1-t0):.2f}s")

    # Generate pairs
    pairs = generate_pairs(normalized)
    print(f"\n[2] Generated {len(pairs)} pairs from {len(test_drugs)} drugs")

    # First run — Cold (hits OpenFDA)
    print(f"\n[3] Cold run (OpenFDA API calls)...")
    t2      = time.time()
    results = await resolve_all_pairs(pairs)
    t3      = time.time()
    cold_ms = int((t3 - t2) * 1000)

    # Enrich with alternatives
    enriched = get_alternatives_for_pairs(results)

    found_count = sum(1 for r in results if r["found"])
    severities  = [r["severity"] for r in results]
    overall     = get_overall_severity(severities)

    print(f"   Time: {cold_ms}ms")
    print(f"   Interactions found: {found_count}/{len(pairs)}")
    print(f"   Overall severity: {overall.upper()} {get_severity_emoji(overall)}")

    print(f"\n   Results:")
    for r in enriched:
        emoji = get_severity_emoji(r["severity"])
        src   = "CACHE" if r.get("from_cache") else "API"
        alts  = r.get("safer_alternatives", [])
        print(
            f"   {emoji} [{src}] {r['drug1']:12} + "
            f"{r['drug2']:12} | {r['severity'].upper()}"
        )
        if alts:
            print(f"      Alternatives: {', '.join(alts)}")

    # Second run — Warm (should all be cached)
    print(f"\n[4] Warm run (from MongoDB cache)...")
    t4       = time.time()
    results2 = await resolve_all_pairs(pairs)
    t5       = time.time()
    warm_ms  = int((t5 - t4) * 1000)

    cache_hits = sum(
        1 for r in results2 if r.get("from_cache")
    )
    print(f"   Time: {warm_ms}ms")
    print(f"   Cache hits: {cache_hits}/{len(pairs)}")

    speedup = cold_ms / warm_ms if warm_ms > 0 else 0
    print(f"   Speedup: {speedup:.1f}x faster")

    # Cache statistics
    stats = await get_cache_stats()
    print(f"\n[5] Cache Statistics:")
    print(f"   Hits:        {stats['hits']}")
    print(f"   Misses:      {stats['misses']}")
    print(f"   Stores:      {stats['stores']}")
    print(f"   Hit rate:    {stats['hit_rate']}")
    print(f"   Total pairs: {stats['total_cached_pairs']}")

    # Performance verdict
    print(f"\n[6] Performance Verdict:")
    if cold_ms < 10000:
        print(f"   ✅ Cold run under 10s ({cold_ms}ms)")
    else:
        print(f"   ⚠️  Cold run slow ({cold_ms}ms) — check API key")

    if warm_ms < 500:
        print(f"   ✅ Warm run under 500ms ({warm_ms}ms)")
    else:
        print(f"   ⚠️  Cache slow ({warm_ms}ms) — check MongoDB")

    if cache_hits == len(pairs):
        print(f"   ✅ All {len(pairs)} pairs served from cache")
    else:
        print(f"   ⚠️  Only {cache_hits}/{len(pairs)} from cache")

    await close_db()
    print("\n" + "=" * 65)
    print("✅ Day 9 Benchmark COMPLETE")
    print("=" * 65)


asyncio.run(benchmark())