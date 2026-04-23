# backend/test_rxnorm_raw.py
# Run this FIRST to confirm what RxNorm actually returns on your machine.
# This has zero dependencies on your app code.

import asyncio
import httpx
import json

RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"


async def check():
    async with httpx.AsyncClient(timeout=10.0) as client:

        print("=" * 55)
        print("RxNorm raw response diagnostic")
        print("=" * 55)

        # ── Test 1: exact match ───────────────────────────────
        print("\n[1] GET /rxcui.json?name=Warfarin&search=1")
        r = await client.get(
            f"{RXNORM_BASE}/rxcui.json",
            params={"name": "Warfarin", "search": "1"}
        )
        print(f"    Status: {r.status_code}")
        data = r.json()
        print(f"    Raw:    {json.dumps(data)}")

        id_group   = data.get("idGroup", {})
        rxnorm_ids = id_group.get("rxnormId")
        print(f"    idGroup.rxnormId → {rxnorm_ids}")

        if rxnorm_ids:
            print(f"    ✅ RxCUI = {rxnorm_ids[0]}")
        else:
            print(f"    ❌ rxnormId is empty — check key path")

        # ── Test 2: approximate match ─────────────────────────
        print("\n[2] GET /approximateTerm.json?term=Aspirin&maxEntries=3")
        r2 = await client.get(
            f"{RXNORM_BASE}/approximateTerm.json",
            params={"term": "Aspirin", "maxEntries": "3"}
        )
        print(f"    Status: {r2.status_code}")
        data2 = r2.json()
        group      = data2.get("approximateGroup", {})
        candidates = group.get("candidate", [])
        print(f"    approximateGroup.candidate count → {len(candidates)}")
        if candidates:
            print(f"    First candidate → {candidates[0]}")
            print(f"    ✅ RxCUI = {candidates[0].get('rxcui')}")
        else:
            print(f"    ❌ No candidates — check key path")

        # ── Test 3: properties for rxcui ─────────────────────
        print("\n[3] GET /rxcui/11289/properties.json  (Warfarin)")
        r3 = await client.get(f"{RXNORM_BASE}/rxcui/11289/properties.json")
        print(f"    Status: {r3.status_code}")
        data3 = r3.json()
        name = data3.get("properties", {}).get("name")
        print(f"    properties.name → '{name}'")

        print("\n" + "=" * 55)
        print("If all 3 show ✅ your normaliser.py key paths are correct.")
        print("If any show ❌ the API returned a different structure.")
        print("=" * 55)


asyncio.run(check())