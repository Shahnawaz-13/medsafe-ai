# test_day13_drugs.py (delete after)
import asyncio
from dotenv import load_dotenv
load_dotenv()

from app.services.normaliser import normalize_drug_list

TWENTY_DRUGS = [
    # Common medications
    "Warfarin",     "Aspirin",       "Metformin",
    "Lisinopril",   "Atorvastatin",  "Omeprazole",
    "Amoxicillin",  "Ibuprofen",     "Paracetamol",
    "Amlodipine",
    # Brand names (should normalize to generic)
    "Coumadin",     "Advil",         "Tylenol",
    "Glucophage",   "Lipitor",       "Prozac",
    # More generics
    "Metoprolol",   "Furosemide",    "Prednisone",
    "Ciprofloxacin",
]


async def test():
    print("=" * 60)
    print("Day 13 — 20 Drug Name Normalization Test")
    print("=" * 60)

    results  = await normalize_drug_list(TWENTY_DRUGS)
    found    = sum(1 for r in results if r["found"])
    not_found = [r for r in results if not r["found"]]

    for r in results:
        status = "✅" if r["found"] else "❌"
        print(
            f"{status} {r['input_name']:15} → "
            f"{r['normalized_name']:20} | "
            f"RxCUI: {r.get('rxcui', 'None')}"
        )

    print(f"\nResult: {found}/20 identified ({int(found/20*100)}%)")

    if not_found:
        print(f"Not found: {[r['input_name'] for r in not_found]}")

    if found >= 17:
        print("✅ Drug normalization test PASSED (85%+)")
    else:
        print("⚠️  Below 85% — review RxNorm integration")

asyncio.run(test())