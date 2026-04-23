# test_mongo_audit.py (delete after running)
import asyncio
from dotenv import load_dotenv
load_dotenv()

from app.database import connect_db, close_db, get_db


async def audit():
    print("=" * 50)
    print("MongoDB Audit")
    print("=" * 50)

    await connect_db()
    db = get_db()

    # Check collections exist
    collections = await db.list_collection_names()
    print(f"\n✅ Collections found: {collections}")

    # Check indexes on drug_cache
    cache_indexes = await db.drug_cache.index_information()
    print(f"\n✅ drug_cache indexes:")
    for name, info in cache_indexes.items():
        print(f"   • {name}: {info.get('key')}")

    # Check indexes on medication_checks
    check_indexes = await db.medication_checks.index_information()
    print(f"\n✅ medication_checks indexes:")
    for name, info in check_indexes.items():
        print(f"   • {name}: {info.get('key')}")

    # Test insert + read + delete
    test_doc = {"test": "day6_audit", "value": 42}
    result   = await db.test_audit.insert_one(test_doc)
    found    = await db.test_audit.find_one(
        {"_id": result.inserted_id}
    )
    await db.test_audit.delete_one({"_id": result.inserted_id})

    print(f"\n✅ Insert/Read/Delete: working")
    print(f"✅ Test document: {found['test']}")

    await close_db()
    print("\n🎉 MongoDB audit PASSED")

asyncio.run(audit())