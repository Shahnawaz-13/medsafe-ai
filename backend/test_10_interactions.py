# test_10_interactions.py (delete after)
import asyncio
import time
from dotenv import load_dotenv
load_dotenv()

from app.database import connect_db, close_db
from app.services.normaliser import normalize_drug_list
from app.services.pair_generator import generate_pairs
from app.services.interaction_resolver import resolve_all_pairs
from app.services.severity_classifier import get_severity_emoji


# 10 known real-world drug interaction pairs
KNOWN_PAIRS = [
    # (drug1, drug2, expected_severity_min)
    ("Warfarin",       "Aspirin",         "moderate"),
    ("Warfarin",       "Ibuprofen",       "moderate"),
    ("Metformin",      "Alcohol",         "moderate"),
    ("Lisinopril",     "Potassium",       "low"),
    ("Simvastatin",    "Clarithromycin",  "high"),
    ("Fluoxetine",     "Tramadol",        "moderate"),
    ("Methotrexate",   "Ibuprofen",       "moderate"),
    ("Digoxin",        "Amiodarone",      "moderate"),
    ("Ciprofloxacin",  "Antacids",        "low"),
    ("Sildenafil",     "Nitroglycerin",   "high"),
]


async def test():
    print("=" * 65)
    print("Day 8 — 10 Known Drug Interaction Test")
    print("=" * 65)

    await connect_db()

    passed = 0
    failed = 0
    errors = 0

    for i, (d1, d2, expected_min) in enumerate(KNOWN_PAIRS, 1):
        try:
            # Normalize
            normalized = await normalize_drug_list([d1, d2])
            pairs      = generate_pairs(normalized)

            if not pairs:
                print(f"\n[{i:02d}] ⚠️  {d1} + {d2}")
                print(f"      Could not generate pair (normalization failed)")
                errors += 1
                continue

            # Resolve
            t_start = time.time()
            results = await resolve_all_pairs(pairs)
            t_end   = time.time()

            r   = results[0]
            sev = r.get("severity", "none")
            emoji = get_severity_emoji(sev)
            src   = "CACHE" if r.get("from_cache") else r.get("source", "API")
            ms    = int((t_end - t_start) * 1000)

            found_str = "FOUND  " if r["found"] else "MISSING"
            print(
                f"\n[{i:02d}] {emoji} {d1} + {d2}"
            )
            print(
                f"      Status:   {found_str} | "
                f"Severity: {sev.upper():<15} | "
                f"Source: {src} | {ms}ms"
            )

            if r["found"]:
                preview = r.get("interaction_text", "")[:100]
                print(f"      Preview:  {preview}...")
                passed += 1
            else:
                print(
                    f"      Note: Not in OpenFDA — "
                    f"may need DrugBank fallback"
                )
                errors += 1

        except Exception as e:
            print(f"\n[{i:02d}] ❌ ERROR: {d1} + {d2}: {e}")
            failed += 1

    await close_db()

    print("\n" + "=" * 65)
    print(f"Results: {passed} found | {errors} not in FDA | {failed} errors")
    print(
        f"Coverage: {passed}/10 pairs resolved "
        f"({int(passed/10*100)}%)"
    )

    if passed >= 6:
        print("✅ Day 8 test PASSED — good OpenFDA coverage")
    else:
        print("⚠️  Coverage below 60% — check API key and strategies")
    print("=" * 65)


asyncio.run(test())