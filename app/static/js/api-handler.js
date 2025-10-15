/**
 * API Handler for External Questions Integration
 * Handles fetching questions from questions.aloc.com.ng API
 */

class QuestionsAPIHandler {
    constructor() {
        this.baseUrl = '/api';
        this.currentQuestions = [];
        this.currentSubject = null;
        this.currentClassLevel = null;
    }

    /**
     * Fetch questions from the API
     * @param {string} subject - Subject name (e.g., 'chemistry', 'physics')
     * @param {string} classLevel - Class level ('ss2' or 'ss3')
     * @param {string} year - Optional year filter
     * @returns {Promise} - Promise that resolves with questions data
     */
    async fetchQuestions(subject, classLevel, year = null) {
        try {
            const url = new URL(`${this.baseUrl}/questions/${subject}/${classLevel}`);
            if (year) {
                url.searchParams.append('year', year);
            }

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.currentQuestions = data.data;
                this.currentSubject = subject;
                this.currentClassLevel = classLevel;
                return data;
            } else {
                throw new Error(data.error || 'Failed to fetch questions');
            }
        } catch (error) {
            console.error('Error fetching questions:', error);
            throw error;
        }
    }

    /**
     * Fetch SS2 Chemistry questions
     * @param {string} year - Optional year filter
     * @returns {Promise} - Promise that resolves with questions data
     */
    async fetchSS2Chemistry(year = null) {
        return this.fetchQuestions('chemistry', 'ss2', year);
    }

    /**
     * Fetch SS3 Chemistry questions
     * @param {string} year - Optional year filter
     * @returns {Promise} - Promise that resolves with questions data
     */
    async fetchSS3Chemistry(year = null) {
        return this.fetchQuestions('chemistry', 'ss3', year);
    }

    /**
     * Fetch SS2 Physics questions
     * @param {string} year - Optional year filter
     * @returns {Promise} - Promise that resolves with questions data
     */
    async fetchSS2Physics(year = null) {
        return this.fetchQuestions('physics', 'ss2', year);
    }

    /**
     * Fetch SS3 Physics questions
     * @param {string} year - Optional year filter
     * @returns {Promise} - Promise that resolves with questions data
     */
    async fetchSS3Physics(year = null) {
        return this.fetchQuestions('physics', 'ss3', year);
    }

    /**
     * Get available subjects
     * @returns {Promise} - Promise that resolves with available subjects
     */
    async getAvailableSubjects() {
        try {
            const response = await fetch(`${this.baseUrl}/subjects`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching subjects:', error);
            throw error;
        }
    }

    /**
     * Test API connection
     * @returns {Promise} - Promise that resolves with test result
     */
    async testConnection() {
        try {
            const response = await fetch(`${this.baseUrl}/test-api`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error testing API connection:', error);
            throw error;
        }
    }

    /**
     * Display questions in a container
     * @param {string} containerId - ID of the container to display questions
     * @param {Array} questions - Array of questions to display
     */
    displayQuestions(containerId, questions = null) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container with ID '${containerId}' not found`);
            return;
        }

        const questionsToDisplay = questions || this.currentQuestions;
        
        if (!questionsToDisplay || questionsToDisplay.length === 0) {
            container.innerHTML = '<p>No questions available.</p>';
            return;
        }

        let html = `
            <div class="questions-container">
                <h3>${this.currentSubject ? this.currentSubject.charAt(0).toUpperCase() + this.currentSubject.slice(1) : 'Questions'} - ${this.currentClassLevel ? this.currentClassLevel.toUpperCase() : ''}</h3>
                <div class="questions-list">
        `;

        questionsToDisplay.forEach((question, index) => {
            html += `
                <div class="question-item" data-question-id="${question.id || index}">
                    <div class="question-text">
                        <strong>Question ${index + 1}:</strong> ${question.question || question.text || 'Question text not available'}
                    </div>
                    <div class="question-options">
                        ${this.renderOptions(question.options || question.option || [])}
                    </div>
                    <div class="question-meta">
                        ${question.year ? `<span class="year">Year: ${question.year}</span>` : ''}
                        ${question.examtype ? `<span class="exam-type">Exam: ${question.examtype}</span>` : ''}
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    /**
     * Render question options
     * @param {Array} options - Array of options
     * @returns {string} - HTML string for options
     */
    renderOptions(options) {
        if (!options || options.length === 0) {
            return '<p>No options available</p>';
        }

        let html = '<div class="options-list">';
        options.forEach((option, index) => {
            const optionText = option.option || option.text || option;
            const isCorrect = option.answer || option.is_correct;
            html += `
                <div class="option-item ${isCorrect ? 'correct-option' : ''}">
                    <span class="option-letter">${String.fromCharCode(65 + index)}.</span>
                    <span class="option-text">${optionText}</span>
                    ${isCorrect ? '<span class="correct-indicator">✓</span>' : ''}
                </div>
            `;
        });
        html += '</div>';
        return html;
    }

    /**
     * Get current questions
     * @returns {Array} - Current questions array
     */
    getCurrentQuestions() {
        return this.currentQuestions;
    }

    /**
     * Clear current questions
     */
    clearQuestions() {
        this.currentQuestions = [];
        this.currentSubject = null;
        this.currentClassLevel = null;
    }
}

// Global instance
window.questionsAPI = new QuestionsAPIHandler();

// Example usage functions
window.loadSS2Chemistry = async function(year = null) {
    try {
        const result = await window.questionsAPI.fetchSS2Chemistry(year);
        console.log('SS2 Chemistry questions loaded:', result);
        return result;
    } catch (error) {
        console.error('Failed to load SS2 Chemistry questions:', error);
        throw error;
    }
};

window.loadSS3Chemistry = async function(year = null) {
    try {
        const result = await window.questionsAPI.fetchSS3Chemistry(year);
        console.log('SS3 Chemistry questions loaded:', result);
        return result;
    } catch (error) {
        console.error('Failed to load SS3 Chemistry questions:', error);
        throw error;
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Questions API Handler initialized');
    
    // Test API connection on page load
    window.questionsAPI.testConnection()
        .then(result => {
            console.log('API connection test:', result);
        })
        .catch(error => {
            console.error('API connection test failed:', error);
        });
});
