"""
Pydantic request / response schemas for the recommendation API.

These models enforce input validation and define the API contract
documented in architecture.md §4.
"""

from pydantic import BaseModel, Field


# ── Request ───────────────────────────────────────────────────
class RecommendRequest(BaseModel):
    """User preferences submitted to POST /api/recommend."""

    location: str = Field(..., min_length=1, description="City or area name")
    budget: str = Field(
        ...,
        pattern="^(low|medium|high)$",
        description="Budget tier: low, medium, or high",
    )
    cuisines: list[str] = Field(
        default=[],
        description="Preferred cuisine types (empty = any)",
    )
    min_rating: float = Field(
        default=0.0,
        ge=0.0,
        le=5.0,
        description="Minimum acceptable rating (0–5)",
    )
    preferences: str = Field(
        default="",
        max_length=500,
        description="Free-text additional preferences",
    )


# ── Response ──────────────────────────────────────────────────
class Recommendation(BaseModel):
    """A single restaurant recommendation returned by the LLM."""

    rank: int
    restaurant_name: str
    cuisines: str
    location: str
    aggregate_rating: float
    average_cost_for_two: int
    explanation: str


class RecommendResponse(BaseModel):
    """Full response for POST /api/recommend."""

    recommendations: list[Recommendation]
    summary: str = ""
    total_candidates_filtered: int = 0
