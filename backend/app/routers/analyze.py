# app/routers/analyze.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/analyze-interaction")
async def analyze_interaction():
    return {"message": "Week 2 — coming soon"}