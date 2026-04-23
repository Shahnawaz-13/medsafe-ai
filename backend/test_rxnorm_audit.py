# test_rxnorm_audit.py (delete after)
import asyncio
from dotenv import load_dotenv
load_dotenv()

from app.services.normaliser import normalize_drug_list


async def audit():
    print("=" * 50)
    print("RxNorm Live Audit — 8 Drug Names")
    print("=" * 50)

    drugs = [
        "Warfarin",       # anticoagulant
        "Aspirin",        # NSAID
        "Metformin",      # diabetes
        "Lisinopril",     # ACE inhibitor
        "Atorvastatin",   # statin
        "Omeprazole",     # PPI
        "Amoxicillin",    # antibiotic
        "xyzfake999",     # fake — should fail
    ]

    results = await normalize_drug_list(drugs)

    found_count = 0
    for r in results:
        status = "✅ FOUND   " if r["found"] else "❌ NOT FOUND"
        print(
            f"{status} | {r['input_name']:15} → "
            f"{r['normalized_name']:15} | "
            f"RxCUI: {r['rxcui']}"
        )
        if r["found"]:
            found_count += 1

    print(f"\nResult: {found_count}/{len(drugs)} drugs identified")

    if found_count >= 7:
        print("✅ RxNorm audit PASSED")
    else:
        print("❌ RxNorm audit FAILED — check API connection")

asyncio.run(audit())