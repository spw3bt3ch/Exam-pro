from flask import Blueprint, jsonify, request, current_app
from .api_service import QuestionsAPIService, SS2_SS3_SUBJECTS
from flask_login import login_required, current_user

api_bp = Blueprint('api', __name__)


@api_bp.route('/questions/<subject>/<class_level>')
@login_required
def get_questions(subject, class_level):
    """
    Get questions for a specific subject and class level (SS2 or SS3)
    
    Args:
        subject: Subject name (chemistry, physics, etc.)
        class_level: Class level (ss2 or ss3)
    """
    if class_level.lower() not in ['ss2', 'ss3']:
        return jsonify({
            'success': False,
            'error': 'Invalid class level. Must be SS2 or SS3'
        }), 400
    
    if subject.lower() not in SS2_SS3_SUBJECTS:
        return jsonify({
            'success': False,
            'error': f'Invalid subject. Available subjects: {list(SS2_SS3_SUBJECTS.keys())}'
        }), 400
    
    # Get year parameter if provided
    year = request.args.get('year')
    
    # Initialize API service
    api_service = QuestionsAPIService()
    
    # Fetch questions based on class level
    if class_level.lower() == 'ss2':
        if subject.lower() == 'chemistry':
            result = api_service.get_ss2_chemistry_questions(year)
        elif subject.lower() == 'physics':
            result = api_service.get_ss2_physics_questions(year)
        elif subject.lower() == 'mathematics':
            result = api_service.get_ss2_mathematics_questions(year)
        elif subject.lower() == 'biology':
            result = api_service.get_ss2_biology_questions(year)
        elif subject.lower() == 'english':
            result = api_service.get_ss2_english_questions(year)
        else:
            result = api_service.fetch_questions(subject, 'utme', year)
    else:  # SS3
        if subject.lower() == 'chemistry':
            result = api_service.get_ss3_chemistry_questions(year)
        elif subject.lower() == 'physics':
            result = api_service.get_ss3_physics_questions(year)
        elif subject.lower() == 'mathematics':
            result = api_service.get_ss3_mathematics_questions(year)
        elif subject.lower() == 'biology':
            result = api_service.get_ss3_biology_questions(year)
        elif subject.lower() == 'english':
            result = api_service.get_ss3_english_questions(year)
        else:
            result = api_service.fetch_questions(subject, 'utme', year)
    
    if result['success']:
        return jsonify({
            'success': True,
            'subject': subject,
            'class_level': class_level.upper(),
            'year': year,
            'data': result['data']
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error'],
            'status_code': result.get('status_code')
        }), 500


@api_bp.route('/subjects')
@login_required
def get_available_subjects():
    """Get list of available subjects for SS2 and SS3"""
    return jsonify({
        'success': True,
        'subjects': SS2_SS3_SUBJECTS,
        'class_levels': ['SS2', 'SS3']
    })


@api_bp.route('/questions/chemistry/ss2')
@login_required
def get_chemistry_ss2():
    """Direct endpoint for SS2 Chemistry questions"""
    return get_questions('chemistry', 'ss2')


@api_bp.route('/questions/chemistry/ss3')
@login_required
def get_chemistry_ss3():
    """Direct endpoint for SS3 Chemistry questions"""
    return get_questions('chemistry', 'ss3')


@api_bp.route('/test-api')
@login_required
def test_api_connection():
    """Test endpoint to verify API connection"""
    api_service = QuestionsAPIService()
    result = api_service.fetch_questions('chemistry', 'utme')
    
    return jsonify({
        'success': result['success'],
        'message': 'API connection test',
        'result': result
    })
