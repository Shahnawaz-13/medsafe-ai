# test_rxnorm.py (temporary — delete after)
import asyncio
from app.services.normaliser import normalize_drug_list

async def test():
    test_drugs = [
        "Warfarin",      # should find immediately
        "aspirin",       # lowercase — should normalize
        "Metformin",     # diabetes drug
        "lisinopril",    # blood pressure
        "atorvastatin",  # statin
        "xyzabc999",     # fake drug — should return not found
    ]

    print("Testing RxNorm normalisation...\n")
    results = await normalize_drug_list(test_drugs)

    for r in results:
        status = "✅ FOUND" if r["found"] else "❌ NOT FOUND"
        print(
            f"{status} | Input: '{r['input_name']}' → "
            f"'{r['normalized_name']}' | RxCUI: {r['rxcui']}"
        )

asyncio.run(test())