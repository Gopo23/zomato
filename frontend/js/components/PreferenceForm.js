// frontend/js/components/PreferenceForm.js

class PreferenceForm {
    constructor(onSubmitCallback) {
        this.form = document.getElementById('preference-form');
        this.locationSelect = document.getElementById('location');
        this.cuisineSelect = document.getElementById('cuisine');
        this.ratingInput = document.getElementById('min-rating');
        this.ratingVal = document.getElementById('rating-val');
        
        this.onSubmitCallback = onSubmitCallback;

        this.initEventListeners();
    }

    initEventListeners() {
        // Update rating display
        this.ratingInput.addEventListener('input', (e) => {
            this.ratingVal.textContent = parseFloat(e.target.value).toFixed(1) + '+';
        });

        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
    }

    /**
     * Populate the location dropdown
     * @param {string[]} locations 
     */
    populateLocations(locations) {
        if (locations.length === 0) {
            this.locationSelect.innerHTML = '<option value="">No locations available</option>';
            return;
        }

        this.locationSelect.innerHTML = '<option value="">Select a location...</option>';
        // Sort alphabetically
        locations.sort().forEach(loc => {
            const option = document.createElement('option');
            option.value = loc;
            option.textContent = loc;
            this.locationSelect.appendChild(option);
        });
    }

    /**
     * Populate the cuisine dropdown
     * @param {string[]} cuisines 
     */
    populateCuisines(cuisines) {
        if (cuisines.length === 0) {
            this.cuisineSelect.innerHTML = '<option value="">No cuisines available</option>';
            return;
        }

        this.cuisineSelect.innerHTML = '<option value="">Any Cuisine...</option>';
        cuisines.sort().forEach(cuisine => {
            const option = document.createElement('option');
            option.value = cuisine;
            option.textContent = cuisine;
            this.cuisineSelect.appendChild(option);
        });
    }

    /**
     * Handle form submission and extract values
     */
    handleSubmit() {
        const formData = new FormData(this.form);
        
        const selectedCuisine = formData.get('cuisine');
        
        const payload = {
            location: formData.get('location'),
            budget: formData.get('budget'),
            cuisines: selectedCuisine ? [selectedCuisine] : [],
            min_rating: parseFloat(formData.get('min_rating')),
            preferences: formData.get('preferences') || ''
        };

        if (this.onSubmitCallback) {
            this.onSubmitCallback(payload);
        }
    }
}
