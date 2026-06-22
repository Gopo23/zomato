// frontend/js/app.js

document.addEventListener('DOMContentLoaded', async () => {
    
    const elements = {
        initialState: document.getElementById('initial-state'),
        loadingState: document.getElementById('loading-state'),
        resultsState: document.getElementById('results-state'),
        cardsContainer: document.getElementById('cards-container'),
        summaryText: document.getElementById('ai-summary-text'),
        submitBtn: document.getElementById('submit-btn')
    };

    // Initialize Form Component
    const form = new PreferenceForm(async (payload) => {
        await handleSearch(payload);
    });

    // Load initial data
    try {
        const [locations, cuisines] = await Promise.all([
            ApiClient.getLocations(),
            ApiClient.getCuisines()
        ]);
        
        form.populateLocations(locations);
        form.populateCuisines(cuisines);
    } catch (err) {
        console.error("Failed to load initial data", err);
        alert("Failed to connect to the server. Is the FastAPI backend running?");
    }

    /**
     * Handles the search workflow
     * @param {Object} payload 
     */
    async function handleSearch(payload) {
        // UI State: Loading
        elements.initialState.classList.add('hidden');
        elements.resultsState.classList.add('hidden');
        elements.loadingState.classList.remove('hidden');
        
        elements.submitBtn.disabled = true;
        elements.submitBtn.textContent = 'Thinking...';

        try {
            const data = await ApiClient.getRecommendations(payload);
            
            // Render Results
            elements.summaryText.textContent = data.summary;
            
            if (data.recommendations && data.recommendations.length > 0) {
                const cardsHtml = data.recommendations
                    .map(rec => RecommendationCard.render(rec))
                    .join('');
                elements.cardsContainer.innerHTML = cardsHtml;
            } else {
                elements.cardsContainer.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #5b403f;">
                        <h3>No matches found</h3>
                        <p>Try relaxing your filters (e.g. lower rating, broader budget).</p>
                    </div>
                `;
            }

            // UI State: Results
            elements.loadingState.classList.add('hidden');
            elements.resultsState.classList.remove('hidden');

        } catch (error) {
            console.error("Search error", error);
            alert("Error fetching recommendations: " + error.message);
            
            // Revert state
            elements.loadingState.classList.add('hidden');
            elements.initialState.classList.remove('hidden');
        } finally {
            elements.submitBtn.disabled = false;
            elements.submitBtn.textContent = 'Ask AI';
        }
    }
});
