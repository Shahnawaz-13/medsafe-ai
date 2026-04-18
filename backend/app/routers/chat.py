# app/routers/chat.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/chat")
async def chat():
    return {"message": "Week 3 — coming soon"}