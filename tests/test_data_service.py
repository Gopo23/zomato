"""Tests for the data ingestion and filtering service.

These tests use a small synthetic DataFrame so they run fast
and without network access.  The DataService constructor is
bypassed — we inject the test frame directly.
"""

import os
import sys

import pandas as pd
import pytest

# Add backend/ to the path so imports work when running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from services.data_service import DataService, BUDGET_TIERS, _MIN_CANDIDATES


# ── Fixtures ──────────────────────────────────────────────────


def _make_sample_df() -> pd.DataFrame:
    """Return a pre-cleaned DataFrame for testing.

    Larger than _MIN_CANDIDATES per group so filters return
    enough rows without triggering relaxation unexpectedly.
    """
    data = [
        # ── Koramangala (4 restaurants) ──
        {
            "restaurant_name": "Pasta Palace",
            "location": "Koramangala",
            "cuisines": "Italian, Continental",
            "average_cost_for_two": 600,
            "aggregate_rating": 4.5,
            "votes": 320,
            "has_online_delivery": True,
            "has_table_booking": True,
            "budget_tier": "medium",
        },
        {
            "restaurant_name": "Dragon Wok",
            "location": "Koramangala",
            "cuisines": "Chinese, Thai",
            "average_cost_for_two": 250,
            "aggregate_rating": 3.8,
            "votes": 150,
            "has_online_delivery": True,
            "has_table_booking": False,
            "budget_tier": "low",
        },
        {
            "restaurant_name": "Cafe Mocha",
            "location": "Koramangala",
            "cuisines": "Cafe, Continental",
            "average_cost_for_two": 350,
            "aggregate_rating": 4.1,
            "votes": 180,
            "has_online_delivery": True,
            "has_table_booking": False,
            "budget_tier": "medium",
        },
        {
            "restaurant_name": "Burger Barn",
            "location": "Koramangala",
            "cuisines": "American, Fast Food",
            "average_cost_for_two": 280,
            "aggregate_rating": 3.9,
            "votes": 220,
            "has_online_delivery": True,
            "has_table_booking": False,
            "budget_tier": "low",
        },
        # ── Indiranagar (3 restaurants) ──
        {
            "restaurant_name": "Biryani Blues",
            "location": "Indiranagar",
            "cuisines": "North Indian, Biryani",
            "average_cost_for_two": 450,
            "aggregate_rating": 4.2,
            "votes": 890,
            "has_online_delivery": True,
            "has_table_booking": False,
            "budget_tier": "medium",
        },
        {
            "restaurant_name": "Dosa Camp",
            "location": "Indiranagar",
            "cuisines": "South Indian",
            "average_cost_for_two": 150,
            "aggregate_rating": 4.0,
            "votes": 200,
            "has_online_delivery": True,
            "has_table_booking": False,
            "budget_tier": "low",
        },
        {
            "restaurant_name": "Taco Bell",
            "location": "Indiranagar",
            "cuisines": "Mexican, Fast Food",
            "average_cost_for_two": 300,
            "aggregate_rating": 3.5,
            "votes": 140,
            "has_online_delivery": True,
            "has_table_booking": False,
            "budget_tier": "low",
        },
        # ── Other locations ──
        {
            "restaurant_name": "Le Jardin",
            "location": "MG Road",
            "cuisines": "French, Continental",
            "average_cost_for_two": 1500,
            "aggregate_rating": 4.8,
            "votes": 450,
            "has_online_delivery": False,
            "has_table_booking": True,
            "budget_tier": "high",
        },
        {
            "restaurant_name": "Sushi Zen",
            "location": "Whitefield",
            "cuisines": "Japanese, Sushi",
            "average_cost_for_two": 900,
            "aggregate_rating": 4.6,
            "votes": 310,
            "has_online_delivery": False,
            "has_table_booking": True,
            "budget_tier": "high",
        },
        {
            "restaurant_name": "Royal Dine",
            "location": "MG Road",
            "cuisines": "North Indian, Mughlai",
            "average_cost_for_two": 1000,
            "aggregate_rating": 4.3,
            "votes": 500,
            "has_online_delivery": False,
            "has_table_booking": True,
            "budget_tier": "high",
        },
    ]
    return pd.DataFrame(data)


@pytest.fixture
def data_service(tmp_path) -> DataService:
    """Create a DataService with a synthetic dataset (no HF download)."""
    # We bypass __init__ to avoid network calls
    svc = object.__new__(DataService)
    svc._cache_path = str(tmp_path / "test_cache.csv")
    svc.df = _make_sample_df()
    return svc


# ── Tests ─────────────────────────────────────────────────────


class TestDataLoading:
    """Tests related to dataset loading & cleaning helpers."""

    def test_parse_rating_normal(self):
        assert DataService._parse_rating("4.5") == 4.5

    def test_parse_rating_with_slash(self):
        assert DataService._parse_rating("4.1/5") == 4.1

    def test_parse_rating_new(self):
        assert DataService._parse_rating("NEW") == 0.0

    def test_parse_rating_dash(self):
        assert DataService._parse_rating("-") == 0.0

    def test_parse_rating_none(self):
        assert DataService._parse_rating(None) == 0.0

    def test_parse_cost_normal(self):
        assert DataService._parse_cost("800") == 800

    def test_parse_cost_with_comma(self):
        assert DataService._parse_cost("1,200") == 1200

    def test_parse_cost_none(self):
        assert DataService._parse_cost(None) == 0

    def test_parse_cost_empty(self):
        assert DataService._parse_cost("") == 0

    def test_cost_to_tier_low(self):
        assert DataService._cost_to_tier(200) == "low"
        assert DataService._cost_to_tier(300) == "low"

    def test_cost_to_tier_medium(self):
        assert DataService._cost_to_tier(301) == "medium"
        assert DataService._cost_to_tier(800) == "medium"

    def test_cost_to_tier_high(self):
        assert DataService._cost_to_tier(801) == "high"
        assert DataService._cost_to_tier(2000) == "high"


class TestFilterByLocation:
    """Test location-based filtering."""

    def test_filter_exact_location(self, data_service: DataService):
        result = data_service.filter_restaurants(location="Koramangala")
        assert len(result) == 4
        assert "Pasta Palace" in result["restaurant_name"].values
        assert "Dragon Wok" in result["restaurant_name"].values

    def test_filter_case_insensitive(self, data_service: DataService):
        result = data_service.filter_restaurants(location="koramangala")
        assert len(result) == 4

    def test_filter_partial_location(self, data_service: DataService):
        result = data_service.filter_restaurants(location="Indira")
        assert len(result) == 3
        assert "Biryani Blues" in result["restaurant_name"].values

    def test_filter_no_match_location(self, data_service: DataService):
        # Will trigger relaxation → returns all restaurants
        result = data_service.filter_restaurants(location="Narnia")
        assert len(result) >= _MIN_CANDIDATES


class TestFilterByBudget:
    """Test budget tier filtering."""

    def test_filter_low_budget(self, data_service: DataService):
        result = data_service.filter_restaurants(budget="low")
        assert len(result) == 4  # Dragon Wok, Burger Barn, Dosa Camp, Taco Bell
        for _, row in result.iterrows():
            assert row["budget_tier"] == "low"

    def test_filter_medium_budget(self, data_service: DataService):
        result = data_service.filter_restaurants(budget="medium")
        assert len(result) == 3  # Pasta Palace, Cafe Mocha, Biryani Blues
        for _, row in result.iterrows():
            assert row["budget_tier"] == "medium"

    def test_filter_high_budget(self, data_service: DataService):
        result = data_service.filter_restaurants(budget="high")
        assert len(result) == 3  # Le Jardin, Sushi Zen, Royal Dine
        for _, row in result.iterrows():
            assert row["budget_tier"] == "high"


class TestFilterByCuisine:
    """Test cuisine-based filtering."""

    def test_filter_single_cuisine(self, data_service: DataService):
        result = data_service.filter_restaurants(cuisines=["Italian"])
        assert "Pasta Palace" in result["restaurant_name"].values

    def test_filter_multiple_cuisines(self, data_service: DataService):
        result = data_service.filter_restaurants(cuisines=["Italian", "Chinese"])
        names = set(result["restaurant_name"])
        assert "Pasta Palace" in names
        assert "Dragon Wok" in names

    def test_filter_cuisine_case_insensitive(self, data_service: DataService):
        result = data_service.filter_restaurants(cuisines=["italian"])
        assert "Pasta Palace" in result["restaurant_name"].values


class TestFilterByRating:
    """Test minimum rating filtering."""

    def test_filter_min_rating(self, data_service: DataService):
        result = data_service.filter_restaurants(min_rating=4.5)
        for _, row in result.iterrows():
            assert row["aggregate_rating"] >= 4.5

    def test_filter_high_rating(self, data_service: DataService):
        result = data_service.filter_restaurants(min_rating=4.7)
        assert len(result) >= 1
        assert "Le Jardin" in result["restaurant_name"].values


class TestCombinedFilters:
    """Test applying multiple filters together."""

    def test_location_and_budget(self, data_service: DataService):
        result = data_service.filter_restaurants(
            location="Koramangala", budget="medium"
        )
        # Only Pasta Palace matches Koramangala + medium
        assert len(result) >= 1

    def test_sorted_by_rating(self, data_service: DataService):
        result = data_service.filter_restaurants()
        ratings = result["aggregate_rating"].tolist()
        assert ratings == sorted(ratings, reverse=True)

    def test_limit_respected(self, data_service: DataService):
        result = data_service.filter_restaurants(limit=3)
        assert len(result) <= 3


class TestFilterRelaxation:
    """Test that filters are relaxed when too few candidates remain."""

    def test_impossible_filters_still_return_results(
        self, data_service: DataService
    ):
        """No restaurant should match this exact combo, so relaxation fires."""
        result = data_service.filter_restaurants(
            location="Koramangala",
            budget="high",
            cuisines=["Japanese"],
            min_rating=4.9,
        )
        # After relaxation we should get *something*
        assert len(result) >= _MIN_CANDIDATES

    def test_relaxation_drops_cuisine_first(self, data_service: DataService):
        """If only cuisine is too restrictive, dropping it should help."""
        # Koramangala + medium + "Martian" cuisine → 0 results
        # After relaxation 1 (drop cuisine): Koramangala + medium → 1 result
        # Still < 3, so further relaxation occurs
        result = data_service.filter_restaurants(
            location="Koramangala",
            budget="medium",
            cuisines=["Martian"],
        )
        assert len(result) >= _MIN_CANDIDATES


class TestGetMetadata:
    """Test helper methods for location/cuisine lists."""

    def test_get_locations(self, data_service: DataService):
        locations = data_service.get_locations()
        assert isinstance(locations, list)
        assert len(locations) == 4  # Indiranagar, Koramangala, MG Road, Whitefield
        assert locations == sorted(locations)

    def test_get_cuisines(self, data_service: DataService):
        cuisines = data_service.get_cuisines()
        assert isinstance(cuisines, list)
        assert "Italian" in cuisines
        assert "Chinese" in cuisines
        assert "South Indian" in cuisines
        assert cuisines == sorted(cuisines)


class TestCleanMethod:
    """Test the static _clean method on raw-style DataFrames."""

    def test_clean_renames_columns(self):
        raw = pd.DataFrame(
            {
                "name": ["Test Place"],
                "location": ["Bengaluru"],
                "cuisines": ["Indian"],
                "approx_cost(for two people)": ["500"],
                "rate": ["4.1/5"],
                "votes": [100],
                "online_order": ["Yes"],
                "book_table": ["No"],
            }
        )
        cleaned = DataService._clean(raw)
        assert "restaurant_name" in cleaned.columns
        assert "aggregate_rating" in cleaned.columns
        assert "average_cost_for_two" in cleaned.columns
        assert cleaned.iloc[0]["aggregate_rating"] == 4.1
        assert cleaned.iloc[0]["average_cost_for_two"] == 500
        assert bool(cleaned.iloc[0]["has_online_delivery"]) is True
        assert bool(cleaned.iloc[0]["has_table_booking"]) is False
        assert cleaned.iloc[0]["budget_tier"] == "medium"

    def test_clean_handles_new_rating(self):
        raw = pd.DataFrame(
            {
                "name": ["New Place"],
                "location": ["Delhi"],
                "cuisines": ["Indian"],
                "approx_cost(for two people)": ["200"],
                "rate": ["NEW"],
                "votes": [0],
                "online_order": ["No"],
                "book_table": ["No"],
            }
        )
        cleaned = DataService._clean(raw)
        assert cleaned.iloc[0]["aggregate_rating"] == 0.0

    def test_clean_drops_empty_names(self):
        raw = pd.DataFrame(
            {
                "name": ["", "Valid"],
                "location": ["Delhi", "Mumbai"],
                "cuisines": ["Indian", "Chinese"],
                "approx_cost(for two people)": ["200", "400"],
                "rate": ["3.5", "4.0"],
                "votes": [10, 20],
                "online_order": ["Yes", "No"],
                "book_table": ["No", "Yes"],
            }
        )
        cleaned = DataService._clean(raw)
        assert len(cleaned) == 1
        assert cleaned.iloc[0]["restaurant_name"] == "Valid"
