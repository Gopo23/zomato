# Zomato AI Recommendation System - Deployment Plan

This document outlines the steps to deploy the application's backend on Railway and the frontend on Vercel.

## 1. Backend Deployment on Railway

The backend is a Python FastAPI application. Railway natively supports Python/FastAPI deployments via Nixpacks, making the process straightforward.

### Prerequisites
- A Railway account (https://railway.app)
- The project pushed to a GitHub repository.

### Steps
1. **Log in to Railway** and click **New Project**.
2. Select **Deploy from GitHub repo** and choose your repository.
3. Configure the Deployment:
   - Go to your newly created service in the Railway dashboard.
   - Under the **Settings** tab, configure the **Root Directory** to `/backend`.
   - Railway will automatically detect the `requirements.txt` file and install dependencies.
   - For the **Start Command**, Railway usually detects Uvicorn automatically, but you can explicitly set it to:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
4. **Environment Variables**:
   - Navigate to the **Variables** tab for the service.
   - Add the necessary environment variables from your local `.env` file, specifically:
     - `GROQ_API_KEY`
     - Any other environment-specific variables used in `config.py`.
5. **Generate a Domain**:
   - Go to the **Settings** tab and under "Networking", click **Generate Domain** to get a public URL for your API (e.g., `https://your-app.up.railway.app`).
   - *Note: Save this URL as you will need it for the frontend configuration.*

---

## 2. Frontend Deployment on Vercel

The frontend is a static HTML/JS/CSS application.

### Prerequisites
- A Vercel account (https://vercel.com)
- The backend deployed and its public URL ready.

### Preparation: Update API Base URL
Before deploying the frontend, you must point the API calls to your newly deployed backend.
1. Open `frontend/js/api.js`.
2. Locate the `API_BASE_URL` constant:
   ```javascript
   const API_BASE_URL = 'http://127.0.0.1:8000/api';
   ```
3. Update it to your Railway backend URL:
   ```javascript
   const API_BASE_URL = 'https://<your-railway-app-url>/api';
   ```
4. Commit and push this change to your repository.

### Steps
1. **Log in to Vercel** and click **Add New Project**.
2. **Import your GitHub repository**.
3. **Configure the Project**:
   - **Framework Preset**: Vercel will likely detect "Other" or you can leave it as default.
   - **Root Directory**: Click "Edit" and select the `frontend` folder.
   - **Build and Output Settings**: Since this is a vanilla HTML/JS project, no build command is needed. Ensure the Output Directory is empty or left as default (it will serve the files directly from the `frontend` directory).
4. **Deploy**: Click the **Deploy** button.
5. Once deployment is finished, Vercel will provide you with a live production URL (e.g., `https://your-frontend-app.vercel.app`).

---

## 3. Final Configuration (CORS)

After deploying your frontend, you must allow its domain to access your backend API to prevent Cross-Origin Resource Sharing (CORS) errors.

1. Go back to your **Railway** dashboard.
2. In your backend service **Variables**, ensure your application's CORS settings allow requests from your Vercel URL.
   - *Note: Looking at `backend/config.py` and `backend/main.py`, the backend reads `cors_origins` from the configuration. You might need to update this list to include your Vercel URL, or if it's currently set to `["*"]`, it will work out of the box (though `["*"]` is less secure for production).*

## 4. Verification
1. Open the Vercel URL in your browser.
2. Open the browser's developer tools (Console and Network tabs).
3. Test the application (e.g., fetching locations, cuisines, and getting recommendations).
4. Verify that requests are successfully reaching the Railway backend and returning data without errors.
