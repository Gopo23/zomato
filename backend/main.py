"""
FastAPI application entry point for the Zomato AI Recommendation System.

Run with:
    uvicorn main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from services.data_service import DataService
from services.llm_service import LLMService
from services.recommendation_service import RecommendationService
from models.schemas import RecommendRequest, RecommendResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)


# ── Lifespan ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    print(f"[*] Starting Zomato AI Recommender (model={settings.groq_model})")
    
    # Phase 2: load the dataset once and attach to app state
    app.state.data_service = DataService(cache_path=settings.dataset_cache_path)
    
    # Phase 3: Initialize LLM and Recommendation services
    app.state.llm_service = LLMService(settings)
    app.state.recommendation_service = RecommendationService(
        data_service=app.state.data_service,
        llm_service=app.state.llm_service
    )
    
    print(
        f"[*] Dataset loaded - {len(app.state.data_service.df)} restaurants, "
        f"{len(app.state.data_service.get_locations())} locations, "
        f"{len(app.state.data_service.get_cuisines())} cuisines"
    )
    
    # Verify Groq API key connectivity
    is_connected = await app.state.llm_service.check_connection()
    if is_connected:
        print("[+] Connected to Groq API successfully.")
    else:
        print("[-] Failed to connect to Groq API. Check your GROQ_API_KEY in .env.")
        
    yield
    print("[*] Shutting down...")


# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="Zomato AI Restaurant Recommendation API",
    description="Intelligent restaurant recommendations powered by Groq LLM.",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Dependencies ──────────────────────────────────────────────
def get_data_service() -> DataService:
    return app.state.data_service

def get_llm_service() -> LLMService:
    return app.state.llm_service
    
def get_recommendation_service() -> RecommendationService:
    return app.state.recommendation_service


# ── Routes ────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Return service health status."""
    return {
        "status": "ok",
        "model": settings.groq_model,
        "version": "0.1.0",
        "llm_connected": await app.state.llm_service.check_connection()
    }


@app.get("/api/locations", tags=["Data"])
@limiter.limit("60/minute")
async def get_locations(request: Request):
    """Get a list of all distinct locations."""
    data_service = get_data_service()
    return data_service.get_locations()


@app.get("/api/cuisines", tags=["Data"])
@limiter.limit("60/minute")
async def get_cuisines(request: Request):
    """Get a list of all distinct cuisines."""
    data_service = get_data_service()
    return data_service.get_cuisines()


@app.post("/api/recommend", response_model=RecommendResponse, tags=["Recommendations"])
@limiter.limit("10/minute")
async def recommend_restaurants(request: Request, payload: RecommendRequest):
    """
    Get AI-powered restaurant recommendations based on preferences.
    """
    rec_service = get_recommendation_service()
    return await rec_service.get_recommendations(payload)
