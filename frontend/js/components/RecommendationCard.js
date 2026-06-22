// frontend/js/components/RecommendationCard.js

class RecommendationCard {
    /**
     * Generates HTML string for a single restaurant card
     * @param {Object} data Recommendation data
     * @returns {string} HTML string
     */
    static render(data) {
        // We are skipping food images per the user's request, so no <img> tag.
        
        return `
            <div class="restaurant-card">
                <div class="rank-badge">${data.rank}</div>
                
                <div class="card-header">
                    <h3 class="restaurant-name">${this.escapeHtml(data.restaurant_name)}</h3>
                    <div class="zomato-rating">
                        <span>${data.aggregate_rating}</span>
                        <span style="font-size: 10px;">★</span>
                    </div>
                </div>
                
                <div class="card-meta">
                    <div class="meta-item">
                        <strong>Cuisines:</strong> ${this.escapeHtml(data.cuisines)}
                    </div>
                    <div class="meta-item">
                        <strong>Location:</strong> ${this.escapeHtml(data.location)}
                    </div>
                    <div class="meta-item">
                        <strong>Cost for two:</strong> ₹${data.average_cost_for_two}
                    </div>
                </div>
                
                <div class="ai-insight-box">
                    <strong>✨ AI Insight:</strong> ${this.escapeHtml(data.explanation)}
                </div>
            </div>
        `;
    }

    // Helper to prevent XSS
    static escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}
