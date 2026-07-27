from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DecisionResponseData(BaseModel):
    risk_level: str = Field(alias="Risk Level")
    confidence_score: float = Field(alias="Confidence Score")
    evidence: List[str] = Field(alias="Evidence")
    reasoning: str = Field(alias="Reasoning")
    priority: str = Field(alias="Priority")
    affected_areas: List[Any] = Field(alias="Affected Areas")
    recommended_actions: List[str] = Field(alias="Recommended Actions")
    sources_used: List[str] = Field(alias="Sources Used")
    emergency_level: bool = Field(alias="Emergency Level")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class DecisionResponse(BaseModel):
    status: str
    data: DecisionResponseData
    summary: str
