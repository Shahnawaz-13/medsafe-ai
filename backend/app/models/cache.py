# app/models/cache.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class DrugCacheModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    pair_key: str
    drug1: str
    drug2: str
    rxcui1: Optional[str] = None
    rxcui2: Optional[str] = None
    interaction_data: Dict[str, Any] = {}
    found: bool = False
    source: str = "OpenFDA"
    cached_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }