# backend/test_resolver_fix.py
import asyncio
from app.services.interaction_resolver import extract_generic_name, resolve_interaction


async def test():

    # ── Test 1: Name extraction ───────────────────────────────────────────────
    print("=== Name extraction ===")
    test_names = [
        "warfarin sodium 1 MG Oral Tablet [Coumadin]",
        "24 HR metformin hydrochloride 1000 MG / saxagliptin 2.5 MG Extended Release Oral Tablet [Kombiglyze]",
        "lisinopril 2.5 MG Oral Tablet [Zestril]",
        "aspirin 325 MG Oral Tablet",
    ]
    for name in test_names:
        generic = extract_generic_name(name)
        print(f"  {name[:55]}... → '{generic}'")

    # ── Test 2: Warfarin + Aspirin (first run → OpenFDA) ─────────────────────
    print("\n=== Warfarin + Aspirin (first run) ===")
    result = await resolve_interaction(
        "warfarin sodium 1 MG Oral Tablet [Coumadin]",
        "aspirin 325 MG Oral Tablet",
        rxcui_a="11289",   # Warfarin RxCUI
        rxcui_b="1191",    # Aspirin RxCUI
    )
    print(f"  Found:      {result['found']}")
    print(f"  Source:     {result['source']}")
    print(f"  From cache: {result.get('from_cache', False)}")
    if result["found"]:
        text = result.get("interaction_text") or ""
        print(f"  Text:       {text[:300]}")

    # ── Test 3: Warfarin + Aspirin (second run → cache) ──────────────────────
    print("\n=== Warfarin + Aspirin (cache run) ===")
    result2 = await resolve_interaction(
        "warfarin sodium 1 MG Oral Tablet [Coumadin]",
        "aspirin 325 MG Oral Tablet",
        rxcui_a="11289",
        rxcui_b="1191",
    )
    print(f"  Found:      {result2['found']}")
    print(f"  Source:     {result2['source']}")
    print(f"  From cache: {result2.get('from_cache', False)}")

    # ── Test 4: Metformin + Lisinopril ───────────────────────────────────────
    print("\n=== Metformin + Lisinopril ===")
    result3 = await resolve_interaction(
        "24 HR metformin hydrochloride 1000 MG Oral Tablet",
        "lisinopril 2.5 MG Oral Tablet [Zestril]",
    )
    print(f"  Found:      {result3['found']}")
    print(f"  Source:     {result3['source']}")

    # ── Test 5: Unknown drug (should not crash) ───────────────────────────────
    print("\n=== Unknown drug (graceful fallback) ===")
    result4 = await resolve_interaction(
        "xyzabc999",
        "aspirin 325 MG Oral Tablet",
    )
    print(f"  Found:      {result4['found']}")
    print(f"  Source:     {result4['source']}")

    print("\n✅ All tests complete.")


asyncio.run(test())