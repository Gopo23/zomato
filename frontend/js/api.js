// frontend/js/api.js

// Automatically switch between local development and production Railway API
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
// IMPORTANT: Once you deploy to Railway, replace the placeholder below with your actual Railway domain!
const PRODUCTION_API_URL = 'https://your-railway-app.up.railway.app/api';

const API_BASE_URL = isLocalhost ? 'http://127.0.0.1:8000/api' : PRODUCTION_API_URL;

class ApiClient {
    /**
     * Fetch all available locations
     * @returns {Promise<string[]>}
     */
    static async getLocations() {
        try {
            const response = await fetch(`${API_BASE_URL}/locations`);
            if (!response.ok) throw new Error('Failed to fetch locations');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return [];
        }
    }

    /**
     * Fetch all available cuisines
     * @returns {Promise<string[]>}
     */
    static async getCuisines() {
        try {
            const response = await fetch(`${API_BASE_URL}/cuisines`);
            if (!response.ok) throw new Error('Failed to fetch cuisines');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return [];
        }
    }

    /**
     * Fetch AI recommendations
     * @param {Object} payload 
     * @returns {Promise<Object>}
     */
    static async getRecommendations(payload) {
        try {
            const response = await fetch(`${API_BASE_URL}/recommend`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                const errData = await response.json().catch(() => null);
                throw new Error(errData?.detail || 'Failed to fetch recommendations');
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
}
