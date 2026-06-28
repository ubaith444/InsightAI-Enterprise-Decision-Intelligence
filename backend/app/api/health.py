from fastapi import APIRouter

from app.core.config import validate_environment

router = APIRouter(tags=["Health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "InsightAI API", "environment": validate_environment()}
