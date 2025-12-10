from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import BFTRequest, BFTResponse
from src.core.pipeline import process_bft
from src.db.base import init_db
from src.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.post(f"{settings.api_prefix}/analyze", response_model=BFTResponse)
def analyze_bft(request: BFTRequest):
    try:
        result = process_bft(bft_id=request.bft_id, text=request.text)
        return BFTResponse(
            bft_id=request.bft_id,
            structured_output=result.structured_output,
            artifacts=result.artifacts,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc