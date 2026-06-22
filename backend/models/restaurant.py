"""
Restaurant data model.

Represents a single restaurant entity from the Zomato dataset.
Used internally by the data service for type-safe handling.
"""

from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    """Internal representation of a restaurant record."""

    restaurant_name: str
    location: str
    cuisines: str = "Not Specified"
    average_cost_for_two: int = 0
    aggregate_rating: float = 0.0
    votes: int = 0
    has_online_delivery: bool = False
    has_table_booking: bool = False
    budget_tier: str = Field(
        default="medium",
        pattern="^(low|medium|high)$",
        description="Computed budget tier based on average_cost_for_two",
    )
