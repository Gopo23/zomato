"""
Data ingestion and filtering service.

Handles loading the Zomato dataset from Hugging Face,
preprocessing, and filtering by user preferences.

Implementation: Phase 2
"""

import logging
import os
import re
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# ── Budget tier boundaries (₹ for two) ─────────────────────────
BUDGET_TIERS = {
    "low": (0, 300),
    "medium": (301, 800),
    "high": (801, float("inf")),
}

# Minimum candidates before relaxation kicks in
_MIN_CANDIDATES = 3


class DataService:
    """Loads, cleans, caches and filters the Zomato restaurant dataset."""

    def __init__(self, cache_path: str):
        """
        Parameters
        ----------
        cache_path : str
            Absolute path where the CSV cache will be stored / loaded from,
            e.g. ``backend/data/zomato_dataset.csv``.
        """
        self._cache_path = cache_path
        self.df: pd.DataFrame = self._load_and_clean()
        logger.info(
            "DataService ready — %d restaurants loaded", len(self.df)
        )

    # ── Public API ────────────────────────────────────────────

    def filter_restaurants(
        self,
        *,
        location: Optional[str] = None,
        budget: Optional[str] = None,
        cuisines: Optional[list[str]] = None,
        min_rating: float = 0.0,
        limit: int = 20,
    ) -> pd.DataFrame:
        """Filter the dataset by user preferences.

        Applies filters in order: location → budget → cuisine → rating.
        If fewer than ``_MIN_CANDIDATES`` remain, filters are relaxed
        progressively (see ``_relax_and_filter``).

        Returns at most *limit* rows sorted by ``aggregate_rating`` desc.
        """
        candidates = self._apply_filters(
            location=location,
            budget=budget,
            cuisines=cuisines,
            min_rating=min_rating,
        )

        # Relax filters when not enough results
        if len(candidates) < _MIN_CANDIDATES:
            candidates = self._relax_and_filter(
                candidates,
                location=location,
                budget=budget,
                cuisines=cuisines,
                min_rating=min_rating,
            )

        # Sort by rating descending, drop duplicates, and limit
        candidates = (
            candidates.sort_values("aggregate_rating", ascending=False)
            .drop_duplicates(subset=["restaurant_name", "location"], keep="first")
            .head(limit)
            .reset_index(drop=True)
        )
        return candidates

    def get_locations(self) -> list[str]:
        """Return sorted list of unique locations."""
        return sorted(self.df["location"].dropna().unique().tolist())

    def get_cuisines(self) -> list[str]:
        """Return sorted list of unique individual cuisines."""
        all_cuisines: set[str] = set()
        for entry in self.df["cuisines"].dropna().unique():
            for c in entry.split(","):
                stripped = c.strip()
                if stripped:
                    all_cuisines.add(stripped)
        return sorted(all_cuisines)

    # ── Private helpers ───────────────────────────────────────

    def _load_and_clean(self) -> pd.DataFrame:
        """Load from cache or Hugging Face, then clean."""
        if os.path.exists(self._cache_path):
            logger.info("Loading dataset from local cache: %s", self._cache_path)
            df = pd.read_csv(self._cache_path)
        else:
            logger.info("Downloading dataset from Hugging Face …")
            df = self._download_from_hf()
            # Ensure directory exists
            os.makedirs(os.path.dirname(self._cache_path), exist_ok=True)
            df.to_csv(self._cache_path, index=False)
            logger.info("Cached dataset to %s", self._cache_path)

        df = self._clean(df)
        return df

    @staticmethod
    def _download_from_hf() -> pd.DataFrame:
        """Download from Hugging Face ``datasets`` library."""
        from datasets import load_dataset  # lazy import — heavy dependency

        ds = load_dataset(
            "ManikaSaini/zomato-restaurant-recommendation",
            split="train",
        )
        return ds.to_pandas()

    @staticmethod
    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        """Normalise column names, types, and drop unusable rows."""

        # ── 1. Rename columns to internal names ──────────────
        rename_map = {
            "name": "restaurant_name",
            "online_order": "has_online_delivery",
            "book_table": "has_table_booking",
            "rate": "aggregate_rating",
            "approx_cost(for two people)": "average_cost_for_two",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        # Keep only the columns we care about
        desired_cols = [
            "restaurant_name",
            "location",
            "cuisines",
            "average_cost_for_two",
            "aggregate_rating",
            "votes",
            "has_online_delivery",
            "has_table_booking",
        ]
        existing_cols = [c for c in desired_cols if c in df.columns]
        df = df[existing_cols].copy()

        # ── 2. Parse ratings ─────────────────────────────────
        if "aggregate_rating" in df.columns:
            df["aggregate_rating"] = df["aggregate_rating"].apply(
                DataService._parse_rating
            )

        # ── 3. Parse cost ────────────────────────────────────
        if "average_cost_for_two" in df.columns:
            df["average_cost_for_two"] = df["average_cost_for_two"].apply(
                DataService._parse_cost
            )

        # ── 4. Boolean columns ───────────────────────────────
        for col in ("has_online_delivery", "has_table_booking"):
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .map({"yes": True, "true": True})
                    .fillna(False)
                    .astype(bool)
                )

        # ── 5. Votes to int ──────────────────────────────────
        if "votes" in df.columns:
            df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype(int)

        # ── 6. Normalize strings ─────────────────────────────
        if "restaurant_name" in df.columns:
            df["restaurant_name"] = df["restaurant_name"].astype(str).str.strip()
        if "location" in df.columns:
            df["location"] = df["location"].apply(DataService._clean_location)
        if "cuisines" in df.columns:
            df["cuisines"] = df["cuisines"].apply(DataService._clean_cuisines)

        # ── 7. Drop rows where critical fields are missing ───
        df = df.dropna(subset=["restaurant_name", "location"]).copy()
        df = df[df["restaurant_name"].str.len() > 0].copy()
        df = df[df["location"].str.len() > 0].copy()

        # ── 8. Add budget_tier column ────────────────────────
        df["budget_tier"] = df["average_cost_for_two"].apply(
            DataService._cost_to_tier
        )

        df = df.reset_index(drop=True)
        return df

    # ── Parsing helpers ───────────────────────────────────────

    @staticmethod
    def _clean_location(val) -> str:
        if pd.isna(val):
            return ""
        s = str(val).strip()
        if "Koramangala" in s:
            return "Koramangala"
        if "Whitefield" in s:
            return "Whitefield"
        return s

    @staticmethod
    def _clean_cuisines(val) -> str:
        if pd.isna(val):
            return ""
        s = str(val).strip()
        # Clean up known duplicate cuisines
        s = s.replace("Afghani", "Afghan")
        return s

    @staticmethod
    def _parse_rating(val) -> float:
        """Convert rating strings like '4.1/5', 'NEW', '-' → float."""
        if pd.isna(val):
            return 0.0
        s = str(val).strip()
        # Handle "4.1/5" format
        if "/" in s:
            s = s.split("/")[0].strip()
        # Try numeric
        try:
            return float(s)
        except ValueError:
            return 0.0

    @staticmethod
    def _parse_cost(val) -> int:
        """Convert cost strings like '800', '1,200' → int."""
        if pd.isna(val):
            return 0
        s = str(val).strip().replace(",", "")
        nums = re.findall(r"\d+", s)
        if nums:
            return int(nums[0])
        return 0

    @staticmethod
    def _cost_to_tier(cost: int) -> str:
        """Map a cost value to 'low', 'medium', or 'high'."""
        for tier, (lo, hi) in BUDGET_TIERS.items():
            if lo <= cost <= hi:
                return tier
        return "high"

    # ── Filtering engine ──────────────────────────────────────

    def _apply_filters(
        self,
        *,
        location: Optional[str],
        budget: Optional[str],
        cuisines: Optional[list[str]],
        min_rating: float,
        df: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """Apply all four filter stages in order."""
        result = df if df is not None else self.df.copy()

        # 1 — Location (case-insensitive substring match)
        if location and not result.empty:
            loc_lower = location.strip().lower()
            result = result[
                result["location"].str.lower().str.contains(loc_lower, na=False)
            ]

        # 2 — Budget tier
        if budget and budget in BUDGET_TIERS and not result.empty:
            result = result[result["budget_tier"] == budget]

        # 3 — Cuisine (any preferred cuisine appears in the row's cuisines)
        if cuisines and not result.empty:
            cuisine_lower = [c.strip().lower() for c in cuisines if c.strip()]
            if cuisine_lower:
                result = result[
                    result["cuisines"]
                    .str.lower()
                    .apply(
                        lambda x: any(c in str(x) for c in cuisine_lower)
                    )
                ]

        # 4 — Minimum rating
        if min_rating > 0 and not result.empty:
            result = result[result["aggregate_rating"] >= min_rating]

        return result

    def _relax_and_filter(
        self,
        current: pd.DataFrame,
        *,
        location: Optional[str],
        budget: Optional[str],
        cuisines: Optional[list[str]],
        min_rating: float,
    ) -> pd.DataFrame:
        """Progressively relax filters until ≥ ``_MIN_CANDIDATES`` found.

        Relaxation order:
        1. Drop cuisine filter
        2. Widen budget tier by ±1 level
        3. Drop location filter (expand to all locations)
        """

        # Relaxation 1 — drop cuisine
        if cuisines:
            logger.debug("Relaxation 1: dropping cuisine filter")
            relaxed = self._apply_filters(
                location=location,
                budget=budget,
                cuisines=None,
                min_rating=min_rating,
            )
            if len(relaxed) >= _MIN_CANDIDATES:
                return relaxed

        # Relaxation 2 — widen budget
        if budget and budget in BUDGET_TIERS:
            adjacent_tiers = self._adjacent_budget_tiers(budget)
            logger.debug(
                "Relaxation 2: widening budget to %s", adjacent_tiers
            )
            relaxed = self._apply_filters(
                location=location,
                budget=None,
                cuisines=None,
                min_rating=min_rating,
            )
            relaxed = relaxed[relaxed["budget_tier"].isin(adjacent_tiers)]
            if len(relaxed) >= _MIN_CANDIDATES:
                return relaxed

        # Relaxation 3 — drop location
        logger.debug("Relaxation 3: dropping location filter")
        relaxed = self._apply_filters(
            location=None,
            budget=budget,
            cuisines=cuisines,
            min_rating=min_rating,
        )
        if len(relaxed) >= _MIN_CANDIDATES:
            return relaxed

        # Final fallback — everything
        logger.debug("Final fallback: returning unfiltered dataset")
        return self._apply_filters(
            location=None, budget=None, cuisines=None, min_rating=0.0
        )

    @staticmethod
    def _adjacent_budget_tiers(tier: str) -> list[str]:
        """Return the given tier plus its neighbours."""
        order = ["low", "medium", "high"]
        try:
            idx = order.index(tier)
        except ValueError:
            return order
        neighbours = {tier}
        if idx > 0:
            neighbours.add(order[idx - 1])
        if idx < len(order) - 1:
            neighbours.add(order[idx + 1])
        return list(neighbours)
