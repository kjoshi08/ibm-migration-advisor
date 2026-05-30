from pydantic import BaseModel
from typing import Optional


class AnalysisRequest(BaseModel):
    client_name: str
    infrastructure_description: str


class AnalysisResponse(BaseModel):
    status: str
    client_name: str
    infra_summary: Optional[dict] = None
    migration_plan: Optional[dict] = None
    eval_scores: Optional[dict] = None
    human_review_needed: bool = False
    error: Optional[str] = None
