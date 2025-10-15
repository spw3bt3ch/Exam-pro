# SS2 & SS3 External Questions API Integration

This document describes the complete integration of the external questions API (questions.aloc.com.ng) for SS2 and SS3 students in the CBTPro application.

## Overview

The integration allows SS2 and SS3 students to access external questions from the questions.aloc.com.ng API, providing a comprehensive question bank for various subjects including Chemistry, Physics, Mathematics, Biology, and English.

## API Configuration

### Original API Call
```javascript
fetch("https://questions.aloc.com.ng/api/v2/q?subject=chemistry", {
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'AccessToken': 'QB-23b20d59287d87f94d94'
    },
    method: "GET",
})
.then(function(res){ console.log(res) })
.catch(function(res){ console.log(res) })
```

### Flask Configuration
The API configuration is stored in `config.py`:

```python
# External API Configuration
QUESTIONS_API_BASE_URL = "https://questions.aloc.com.ng/api/v2/q"
QUESTIONS_API_TOKEN = os.environ.get("QUESTIONS_API_TOKEN", "QB-23b20d59287d87f94d94")
QUESTIONS_API_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'AccessToken': QUESTIONS_API_TOKEN
}
```

## Files Created/Modified

### 1. Configuration Files
- **`config.py`** - Added API configuration settings
- **`requirements.txt`** - Added `requests==2.31.0` dependency

### 2. Backend Files
- **`app/api_service.py`** - Service class for handling external API calls
- **`app/api.py`** - Flask blueprint with API routes
- **`app/student.py`** - Added external questions route
- **`app/__init__.py`** - Registered API blueprint

### 3. Frontend Files
- **`app/static/js/api-handler.js`** - JavaScript class for API interactions
- **`app/templates/student/external_questions.html`** - UI for SS2/SS3 questions
- **`app/templates/base.html`** - Added navigation link for SS2/SS3 students

### 4. Test Files
- **`test_api_integration.py`** - Comprehensive API integration test
- **`api_example.html`** - Standalone HTML example

## API Service Features

### QuestionsAPIService Class
Located in `app/api_service.py`, this class provides:

- **Generic question fetching**: `fetch_questions(subject, exam_type, year)`
- **SS2 specific methods**: `get_ss2_chemistry_questions()`, `get_ss2_physics_questions()`, etc.
- **SS3 specific methods**: `get_ss3_chemistry_questions()`, `get_ss3_physics_questions()`, etc.
- **Error handling**: Comprehensive error handling with detailed error messages
- **Timeout management**: 30-second timeout for API requests

### Available Subjects
The integration supports the following subjects for SS2 and SS3:

- Chemistry
- Physics
- Mathematics
- Biology
- English Language
- Economics
- Government
- Literature in English
- Geography
- History
- Commerce
- Accounting
- Further Mathematics
- Agricultural Science
- Christian Religious Studies
- Islamic Religious Studies

## API Routes

### Main Routes
- **`/api/questions/<subject>/<class_level>`** - Get questions for specific subject and class level
- **`/api/subjects`** - Get list of available subjects
- **`/api/test-api`** - Test API connection

### Direct Routes
- **`/api/questions/chemistry/ss2`** - Direct SS2 Chemistry questions
- **`/api/questions/chemistry/ss3`** - Direct SS3 Chemistry questions

### Student Interface
- **`/student/external-questions`** - Main interface for SS2/SS3 students

## Frontend Integration

### JavaScript API Handler
The `QuestionsAPIHandler` class provides:

- **Async/await support**: Modern JavaScript for API calls
- **Question display**: Dynamic rendering of questions and options
- **Error handling**: User-friendly error messages
- **Loading states**: Visual feedback during API calls
- **Year filtering**: Optional year-based question filtering

### User Interface Features
- **Class level selection**: SS2 or SS3 buttons
- **Subject selection**: Grid of available subjects
- **Year filtering**: Dropdown for year selection
- **Question display**: Formatted questions with options and correct answers
- **API testing**: Built-in connection test functionality

## Usage Examples

### 1. Using the Flask API Routes
```python
# In your Flask application
from app.api_service import QuestionsAPIService

api_service = QuestionsAPIService()
result = api_service.get_ss2_chemistry_questions()
if result['success']:
    questions = result['data']
    # Process questions
```

### 2. Using the JavaScript API Handler
```javascript
// Load SS2 Chemistry questions
const result = await window.questionsAPI.fetchSS2Chemistry();
if (result.success) {
    window.questionsAPI.displayQuestions('container-id', result.data);
}

// Load SS3 Physics questions with year filter
const result = await window.questionsAPI.fetchSS3Physics('2024');
```

### 3. Direct API Calls
```javascript
// Direct fetch call (as in your original example)
fetch("https://questions.aloc.com.ng/api/v2/q?subject=chemistry", {
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'AccessToken': 'QB-23b20d59287d87f94d94'
    },
    method: "GET",
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error(error));
```

## Testing

### Running the Integration Test
```bash
python test_api_integration.py
```

The test verifies:
- ✅ API connection
- ✅ All subject availability
- ✅ Year filtering
- ✅ Response structure
- ✅ Error handling

### Test Results
```
🚀 SS2 & SS3 API Integration Test
==================================================
✅ API connection successful!
✅ Successful subjects: chemistry, physics, mathematics, biology, english
📚 Total questions available: 48
✅ Integration appears to be working correctly!
```

## Security Considerations

1. **API Token**: The access token is configurable via environment variable
2. **Authentication**: All routes require user login
3. **Class Level Access**: External questions are only available to SS2 and SS3 students
4. **Error Handling**: Sensitive information is not exposed in error messages

## Environment Variables

Add to your `.env` file:
```env
QUESTIONS_API_TOKEN=QB-23b20d59287d87f94d94
```

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export QUESTIONS_API_TOKEN="QB-23b20d59287d87f94d94"
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the interface**:
   - Navigate to `/student/external-questions`
   - Available only to SS2 and SS3 students

## API Response Structure

The external API returns data in the following format:
```json
{
    "subject": "chemistry",
    "status": 200,
    "data": {
        "1": {
            "question": "What is the chemical symbol for water?",
            "option": [
                {"option": "H2O", "answer": true},
                {"option": "CO2", "answer": false},
                {"option": "NaCl", "answer": false},
                {"option": "O2", "answer": false}
            ],
            "year": "2024",
            "examtype": "utme"
        }
    }
}
```

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check internet connection
   - Verify API token is correct
   - Check if questions.aloc.com.ng is accessible

2. **No Questions Displayed**
   - Verify subject name is correct
   - Check if questions are available for the selected year
   - Review browser console for JavaScript errors

3. **Authentication Issues**
   - Ensure user is logged in
   - Verify user has SS2 or SS3 class level
   - Check Flask session configuration

### Debug Mode
Enable debug mode in Flask to see detailed error messages:
```python
app.run(debug=True)
```

## Future Enhancements

1. **Caching**: Implement Redis caching for frequently accessed questions
2. **Offline Mode**: Store questions locally for offline access
3. **Question Import**: Allow teachers to import external questions into local database
4. **Analytics**: Track question usage and performance metrics
5. **Custom Filters**: Add more filtering options (difficulty, topic, etc.)

## Support

For issues or questions regarding the SS2/SS3 API integration:
1. Check the test results: `python test_api_integration.py`
2. Review the browser console for JavaScript errors
3. Check Flask application logs
4. Verify API token and network connectivity

---

**Integration Status**: ✅ Complete and Tested
**Last Updated**: October 11, 2025
**API Version**: v2
**Supported Classes**: SS2, SS3
