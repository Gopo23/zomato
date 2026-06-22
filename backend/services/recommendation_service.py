"""
Recommendation orchestrator service.

Coordinates the data service (filtering) and LLM service (ranking)
to produce the final recommendation response.

Implementation: Phase 3
"""

import logging
from typing import Dict, Any

from models.schemas import RecommendRequest, RecommendResponse, Recommendation
from services.data_service import DataService
from services.llm_service import LLMService
from prompts.recommend import RECOMMEND_PROMPT
import pandas as pd
import hashlib
import time

class RecommendationCache:
    def __init__(self, ttl_seconds=3600):
        self._cache = {}
        self._ttl = ttl_seconds

    def _key(self, request: RecommendRequest) -> str:
        data = request.model_dump()
        # Sort keys to ensure consistent hashing
        sorted_items = tuple(sorted((k, tuple(v) if isinstance(v, list) else v) for k, v in data.items()))
        return hashlib.sha256(str(sorted_items).encode()).hexdigest()

    def get(self, request: RecommendRequest):
        key = self._key(request)
        if key in self._cache:
            entry, ts = self._cache[key]
            if time.time() - ts < self._ttl:
                return entry
            del self._cache[key]
        return None

    def set(self, request: RecommendRequest, result: RecommendResponse):
        self._cache[self._key(request)] = (result, time.time())

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, data_service: DataService, llm_service: LLMService):
        self.data_service = data_service
        self.llm_service = llm_service
        self.cache = RecommendationCache(ttl_seconds=3600)

    async def get_recommendations(self, request: RecommendRequest) -> RecommendResponse:
        """
        Orchestrates the recommendation flow:
        1. Filter dataset using DataService.
        2. Format candidates into a table for the LLM.
        3. Call LLMService to rank and explain.
        4. Assemble the final response.
        """
        logger.info(f"Processing recommendation request: {request.model_dump()}")
        
        # Check cache first
        cached_response = self.cache.get(request)
        if cached_response:
            logger.info("Returning cached recommendations")
            return cached_response
        
        # 1. Filter candidates (DataService handles relaxation if needed)
        candidates_df = self.data_service.filter_restaurants(
            location=request.location,
            budget=request.budget,
            cuisines=request.cuisines,
            min_rating=request.min_rating,
            limit=20 # Max 20 candidates to fit in context window
        )
        
        total_candidates = len(candidates_df)
        logger.info(f"Found {total_candidates} candidates after filtering")

        # Handle edge case: absolutely no candidates even after relaxation
        if total_candidates == 0:
            return RecommendResponse(
                recommendations=[],
                summary="We couldn't find any restaurants matching your criteria, even after broadening the search. Try a completely different location.",
                total_candidates_filtered=0
            )

        # 2. Build the prompt
        formatted_table = self._format_candidates_table(candidates_df)
        
        # Determine budget max for the prompt
        budget_max_map = {"low": 300, "medium": 800, "high": "No Limit"}
        budget_max = budget_max_map.get(request.budget, 800)
        
        # Sanitize user preferences to prevent prompt injection
        import re
        safe_prefs = request.preferences or "None"
        if safe_prefs != "None":
            # Keep only alphanumeric and basic punctuation, limit to 200 chars
            safe_prefs = re.sub(r'[^\w\s,\.\-\']', '', safe_prefs)[:200]
        
        prompt = RECOMMEND_PROMPT.format(
            location=request.location,
            budget_label=request.budget.title(),
            budget_max=budget_max,
            cuisines=", ".join(request.cuisines) if request.cuisines else "Any",
            min_rating=request.min_rating,
            preferences=safe_prefs,
            formatted_table=formatted_table
        )
        
        logger.debug(f"Generated Prompt:\n{prompt}")

        # 3. Call the LLM
        recommendations = await self.llm_service.get_recommendations(prompt)
        
        # Deduplicate recommendations by restaurant_name and location
        if recommendations:
            seen = set()
            unique_recs = []
            for rec in recommendations:
                key = (rec.restaurant_name.strip().lower(), rec.location.strip().lower())
                if key not in seen:
                    seen.add(key)
                    unique_recs.append(rec)
            recommendations = unique_recs
            
        # 4. Handle fallback if LLM failed completely
        if not recommendations:
            logger.warning("LLM returned no valid recommendations. Falling back to simple ranking.")
            recommendations = self._create_fallback_recommendations(candidates_df)
            summary = "We are currently experiencing high load. Here are the top rated restaurants matching your criteria."
        else:
            recommendations = recommendations[:5]
            summary = f"Here are the top {len(recommendations)} recommendations tailored to your preferences."

        # 5. Assemble and return response
        response = RecommendResponse(
            recommendations=recommendations,
            summary=summary,
            total_candidates_filtered=total_candidates
        )
        
        # Save to cache only if LLM succeeded (not fallback)
        if recommendations and "high load" not in summary.lower():
            self.cache.set(request, response)
            
        return response

    def _format_candidates_table(self, df: pd.DataFrame) -> str:
        """Format the DataFrame as a Markdown table for the LLM."""
        # Select columns relevant for the LLM to make a decision
        cols = [
            "restaurant_name", 
            "cuisines", 
            "location", 
            "aggregate_rating", 
            "average_cost_for_two"
        ]
        
        # Ensure we only use columns that exist
        available_cols = [c for c in cols if c in df.columns]
        
        # Create a markdown table representation
        markdown_table = df[available_cols].to_markdown(index=False)
        return markdown_table
        
    def _create_fallback_recommendations(self, df: pd.DataFrame) -> list[Recommendation]:
        """Create a simple ranked list if the LLM fails."""
        recs = []
        # Take top 5 unique by restaurant name and location
        top_5 = df.drop_duplicates(subset=["restaurant_name", "location"]).head(5)
        
        for idx, row in top_5.iterrows():
            recs.append(
                Recommendation(
                    rank=len(recs) + 1,
                    restaurant_name=str(row.get("restaurant_name", "Unknown")),
                    cuisines=str(row.get("cuisines", "Not specified")),
                    location=str(row.get("location", "Unknown")),
                    aggregate_rating=float(row.get("aggregate_rating", 0.0)),
                    average_cost_for_two=int(row.get("average_cost_for_two", 0)),
                    explanation="High rating in your preferred category."
                )
            )
        return recs
