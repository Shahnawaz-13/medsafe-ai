# app/routers/upload.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/upload-prescription")
async def upload_prescription():
    return {"message": "Week 3 — coming soon"}