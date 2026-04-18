# app/routers/drug_info.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/drug-info")
async def drug_info():
    return {"message": "Week 2 — coming soon"}

@router.get("/drug-autocomplete")
async def drug_autocomplete():
    return {"suggestions": []}