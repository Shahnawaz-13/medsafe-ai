# test_day5.py (temporary — delete after)
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.services.normaliser import normalize_drug_list
from app.services.pair_generator import generate_pairs
from app.services.interaction_resolver import resolve_all_pairs
from app.services.severity_classifier import (
    classify_severity,
    get_overall_severity,
    get_severity_emoji,
)
from app.database import connect_db, close_db


async def test_full_pipeline():
    print("=" * 60)
    print("MedSafe AI — Day 5 Full Pipeline Test")
    print("=" * 60)

    # Connect DB
    print("\n[1] Connecting to MongoDB...")
    await connect_db()
    print("✅ MongoDB connected")

    # Test drugs
    test_drugs = ["Warfarin", "Aspirin", "Metformin", "Lisinopril"]
    print(f"\n[2] Normalising {len(test_drugs)} drugs via RxNorm...")

    normalized = await normalize_drug_list(test_drugs)
    for r in normalized:
        status = "✅" if r["found"] else "❌"
        print(
            f"   {status} {r['input_name']:15} → "
            f"{r['normalized_name']:15} | RxCUI: {r['rxcui']}"
        )

    # Generate pairs
    print(f"\n[3] Generating drug pairs...")
    pairs = generate_pairs(normalized)
    print(f"   ✅ {len(pairs)} pairs generated")
    for a, b in pairs:
        print(
            f"      • {a['normalized_name']} "
            f"+ {b['normalized_name']}"
        )

    # Resolve interactions (hits OpenFDA + cache)
    print(f"\n[4] Resolving interactions via OpenFDA...")
    print("   (First run hits API. Repeat run uses cache.)\n")

    results = await resolve_all_pairs(pairs)

    interactions_found = 0
    severities = []

    for r in results:
        found  = r["found"]
        cached = r.get("from_cache", False)
        source = "CACHE" if cached else r.get("source", "API")
        sev    = r.get("severity", "none")
        emoji  = get_severity_emoji(sev)

        severities.append(sev)

        if found:
            interactions_found += 1
            print(
                f"   {emoji} [{source}] "
                f"{r['drug1']} + {r['drug2']}"
            )
            print(
                f"      Severity: {sev.upper()}"
            )
            # Show first 150 chars of interaction text
            text = r.get("interaction_text", "")[:150]
            print(f"      Text preview: {text}...\n")
        else:
            print(
                f"   ⚪ [{source}] "
                f"{r['drug1']} + {r['drug2']} "
                f"— No interaction found\n"
            )

    # Overall severity
    overall = get_overall_severity(severities)
    print(f"[5] Overall severity: {overall.upper()} "
          f"{get_severity_emoji(overall)}")
    print(f"    Interactions found: {interactions_found}/{len(pairs)}")

    # Test cache — run again and verify cache hits
    print(f"\n[6] Testing cache (re-running same pairs)...")
    cached_results = await resolve_all_pairs(pairs)
    cache_hits = sum(
        1 for r in cached_results if r.get("from_cache")
    )
    print(f"   ✅ Cache hits: {cache_hits}/{len(pairs)}")
    if cache_hits == len(pairs):
        print("   🎉 All pairs served from cache!")

    await close_db()
    print("\n" + "=" * 60)
    print("✅ Day 5 pipeline test COMPLETE")
    print("=" * 60)


asyncio.run(test_full_pipeline())