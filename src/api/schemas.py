from typing import Optional, Dict, Any
from pydantic import BaseModel

class BFTRequest(BaseModel):
    bft_id: str
    text: str

class BFTResponse(BaseModel):
    bft_id: str
    structured_output: Dict[str, Any]
    artifacts: Dict[str, Any]