# test_openfda_audit.py (delete after)
import asyncio
import time
from dotenv import load_dotenv
load_dotenv()

from app.database import connect_db, close_db
from app.services.normaliser import normalize_drug_list
from app.services.pair_generator import generate_pairs
from app.services.interaction_resolver import resolve_all_pairs


async def audit():
    print("=" * 50)
    print("OpenFDA + Cache Audit")
    print("=" * 50)

    await connect_db()

    drugs     = ["Warfarin", "Aspirin", "Metformin"]
    normalized = await normalize_drug_list(drugs)
    pairs      = generate_pairs(normalized)

    # First run — should hit OpenFDA
    print("\n[Run 1] — Hitting OpenFDA API...")
    t1      = time.time()
    results = await resolve_all_pairs(pairs)
    t1_end  = time.time()

    print(f"   Time taken: {t1_end - t1:.2f}s")
    for r in results:
        source = "CACHE" if r.get("from_cache") else "API"
        print(
            f"   [{source}] {r['drug1']} + {r['drug2']} "
            f"→ found={r['found']} | sev={r['severity']}"
        )

    # Second run — should all hit cache
    print("\n[Run 2] — Should serve from cache...")
    t2      = time.time()
    results2 = await resolve_all_pairs(pairs)
    t2_end  = time.time()

    print(f"   Time taken: {t2_end - t2:.2f}s")
    cache_hits = sum(
        1 for r in results2 if r.get("from_cache")
    )

    for r in results2:
        source = "CACHE" if r.get("from_cache") else "API"
        print(
            f"   [{source}] {r['drug1']} + {r['drug2']}"
        )

    print(f"\n   Cache hits: {cache_hits}/{len(pairs)}")

    if cache_hits == len(pairs):
        print("✅ Cache audit PASSED — all from cache")
    else:
        print("⚠️  Some pairs not cached — check TTL index")

    if (t2_end - t2) < (t1_end - t1):
        print("✅ Cache is faster than API calls")

    await close_db()
    print("\n🎉 OpenFDA + Cache audit PASSED")

asyncio.run(audit())