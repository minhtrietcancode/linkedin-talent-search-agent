from typing import List
from pydantic import BaseModel, Field, field_validator

class JDAnalysisResult(BaseModel):
    """Pydantic model for structured JD analysis output"""
    title: str = Field(description="Job title extracted from the job description")
    minimum_degree: str = Field(
        description="Minimum degree requirement",
        pattern="^(None|Diploma|Bachelor|Master|PhD)$"
    )
    location: str = Field(description="Job location")
    skills: List[str] = Field(description="List of required skills/technologies")
    experience: int = Field(description="Minimum years of experience required", ge=0)
    search_keywords: List[str] = Field(description="Keywords for searching candidates")
    workright_requirement: str = Field(description="Work authorization requirements")
    
    @field_validator('minimum_degree')
    @classmethod
    def validate_degree(cls, v):
        valid_degrees = ["None", "Diploma", "Bachelor", "Master", "PhD"]
        if v not in valid_degrees:
            return "None"
        return v 