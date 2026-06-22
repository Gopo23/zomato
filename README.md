# Zomato AI Restaurant Recommender

An AI-powered restaurant recommendation service inspired by Zomato. The system intelligently suggests restaurants based on user preferences by combining structured Zomato dataset data with a Large Language Model (Groq LLaMA/Mixtral).

## Features
- **Smart Filtering:** Pre-filters the massive Zomato dataset using Pandas based on Location, Budget, Cuisine, and Rating.
- **AI Recommendations:** Uses Groq's high-speed inference to rank restaurants and provide human-readable, personalized explanations.
- **Fail-Safe Fallbacks:** Gracefully falls back to offline ranking algorithms if the LLM service is unavailable or rate-limited.
- **Zomato Inspired UI:** A sleek, Light Theme frontend using Vanilla JS/HTML/CSS that perfectly mimics Zomato's brand aesthetics.
- **Robust API:** Built with FastAPI, featuring SlowAPI rate limiting, Response Caching, and prompt injection protections.

## Project Structure
- `backend/` - The FastAPI backend, Groq LLM integration, and Pandas data layer.
- `frontend/` - The Vanilla JS/HTML/CSS Single Page Application.
- `Docs/` - Architecture and planning documentation.

## Requirements
- Python 3.10+
- An API Key from [Groq](https://console.groq.com/keys)

## Setup & Run Instructions

### 1. Backend Setup
1. Open a terminal and navigate to the project directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Copy `.env.example` to `.env` (or create one):
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   DATASET_CACHE_PATH=data/zomato_dataset.csv
   ```
5. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   *Note: On the very first run, it will automatically download the 15MB Zomato dataset from Hugging Face.*

### 2. Frontend Setup
The frontend uses standard HTML/CSS/JS and requires no build step.
1. Make sure your FastAPI backend is running on `http://127.0.0.1:8000`.
2. Simply open `frontend/index.html` in your web browser. 
   - Alternatively, serve it via VS Code Live Server or python's HTTP server:
     ```bash
     cd frontend
     python -m http.server 3000
     ```

## API Documentation
Once the backend is running, you can explore the interactive API documentation and test the endpoints directly at:
- Swagger UI: `http://127.0.0.1:8000/docs`

## Tests
To run the automated test suite (Unit and Integration tests):
```bash
cd backend
pytest tests/ -v
```
