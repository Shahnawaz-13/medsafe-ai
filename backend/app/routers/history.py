# app/routers/history.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/history")
async def get_history():
    return {"checks": [], "total": 0}