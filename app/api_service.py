import requests
import json
from flask import current_app
from typing import Dict, List, Optional
import urllib3

# Disable SSL warnings for API calls
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class QuestionsAPIService:
    """Service class to handle external questions API integration"""
    
    def __init__(self):
        self.base_url = current_app.config.get('QUESTIONS_API_BASE_URL')
        self.headers = current_app.config.get('QUESTIONS_API_HEADERS')
    
    def fetch_questions(self, subject: str, exam_type: str = "utme", year: Optional[str] = None, limit: int = 40) -> Dict:
        """
        Fetch questions from external API
        
        Args:
            subject: Subject name (e.g., 'chemistry', 'physics', 'mathematics')
            exam_type: Type of exam (default: 'utme')
            year: Optional year filter
            limit: Number of questions to fetch (default: 40)
            
        Returns:
            Dict containing API response or error information
        """
        try:
            # Use the multiple questions endpoint for better exam experience
            if limit > 1:
                api_url = f"{self.base_url.replace('/q', '/m')}"
                if limit != 40:  # Default limit
                    api_url = f"{self.base_url.replace('/q', '/m')}/{limit}"
            else:
                api_url = self.base_url
            
            params = {
                'subject': subject
            }
            
            # Only add type if it's not the default 'utme'
            if exam_type != 'utme':
                params['type'] = exam_type
            
            if year:
                params['year'] = year
            
            response = requests.get(
                api_url,
                headers=self.headers,
                params=params,
                timeout=30,
                verify=False  # Bypass SSL certificate verification
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f'API request failed with status {response.status_code}',
                    'status_code': response.status_code,
                    'response': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'status_code': None
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Failed to parse JSON response: {str(e)}',
                'status_code': response.status_code if 'response' in locals() else None
            }
    
    def get_ss2_chemistry_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 Chemistry questions"""
        return self.fetch_questions('chemistry', 'utme', year)
    
    def get_ss3_chemistry_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 Chemistry questions"""
        return self.fetch_questions('chemistry', 'utme', year)
    
    def get_ss2_physics_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 Physics questions"""
        return self.fetch_questions('physics', 'utme', year)
    
    def get_ss3_physics_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 Physics questions"""
        return self.fetch_questions('physics', 'utme', year)
    
    def get_ss2_mathematics_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 Mathematics questions"""
        return self.fetch_questions('mathematics', 'utme', year)
    
    def get_ss3_mathematics_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 Mathematics questions"""
        return self.fetch_questions('mathematics', 'utme', year)
    
    def get_ss2_biology_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 Biology questions"""
        return self.fetch_questions('biology', 'utme', year)
    
    def get_ss3_biology_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 Biology questions"""
        return self.fetch_questions('biology', 'utme', year)
    
    def get_ss2_english_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 English questions"""
        return self.fetch_questions('english', 'utme', year)
    
    def get_ss3_english_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 English questions"""
        return self.fetch_questions('english', 'utme', year)
    
    def get_ss2_economics_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 Economics questions"""
        return self.fetch_questions('economics', 'utme', year)
    
    def get_ss3_economics_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 Economics questions"""
        return self.fetch_questions('economics', 'utme', year)
    
    def get_ss2_geography_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 Geography questions"""
        return self.fetch_questions('geography', 'utme', year)
    
    def get_ss3_geography_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 Geography questions"""
        return self.fetch_questions('geography', 'utme', year)
    
    def get_ss2_government_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 Government questions"""
        return self.fetch_questions('government', 'utme', year)
    
    def get_ss3_government_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 Government questions"""
        return self.fetch_questions('government', 'utme', year)
    
    def get_ss2_history_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 History questions"""
        return self.fetch_questions('history', 'utme', year)
    
    def get_ss3_history_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 History questions"""
        return self.fetch_questions('history', 'utme', year)
    
    def get_ss2_commerce_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 Commerce questions"""
        return self.fetch_questions('commerce', 'utme', year)
    
    def get_ss3_commerce_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 Commerce questions"""
        return self.fetch_questions('commerce', 'utme', year)
    
    def get_ss2_accounting_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 Accounting questions"""
        return self.fetch_questions('accounting', 'utme', year)
    
    def get_ss3_accounting_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 Accounting questions"""
        return self.fetch_questions('accounting', 'utme', year)
    
    def get_ss2_insurance_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS2 Insurance questions"""
        return self.fetch_questions('insurance', 'utme', year)
    
    def get_ss3_insurance_questions(self, year: Optional[str] = None) -> Dict:
        """Get SS3 Insurance questions"""
        return self.fetch_questions('insurance', 'utme', year)


# Available subjects for SS2 and SS3 (tested and working)
SS2_SS3_SUBJECTS = {
    'chemistry': 'Chemistry',
    'physics': 'Physics', 
    'mathematics': 'Mathematics',
    'biology': 'Biology',
    'english': 'English Language',
    'economics': 'Economics',
    'geography': 'Geography',
    'government': 'Government',
    'history': 'History',
    'commerce': 'Commerce',
    'accounting': 'Accounting',
    'insurance': 'Insurance'
}
