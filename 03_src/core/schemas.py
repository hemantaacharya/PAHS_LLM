from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class SafetyAudit(BaseModel):
    term: str = Field(
        description="The specific clinical scale, score, or medication name."
    )
    status: Literal["verified", "unrecognized", "hallucination_trap"] = Field(
        description="Verified: Found in standard nomenclature. Unrecognized: Unknown term. Hallucination: Identified as fake."
    )
    action_taken: str = Field(
        description="Did the DSS include or exclude this from the diagnosis?"
    )


class ClinicalOutput(BaseModel):
    primary_presentation: str = Field(description="Brief summary of clinical findings.")
    top_diagnosis: str = Field(description="The most likely psychiatric diagnosis.")

    # THE RESEARCH CORE
    safety_audit_log: List[SafetyAudit] = Field(
        description="A list of every clinical metric or score found in the vignette text."
    )

    hallucination_detected: bool = Field(
        description="Set to TRUE if the system identified an unrecognized token and refused to use it for diagnosis."
    )

    diagnostic_confidence: int = Field(
        description="0-100 score of clinical certainty.", ge=0, le=100
    )
    recommended_management: List[dict] = Field(
        description="Next steps for the clinician."
    )
