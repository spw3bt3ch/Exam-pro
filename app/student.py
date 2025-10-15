from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response, current_app
from flask_login import login_required, current_user
from .models import User, Subject, Question, Option, ExamSession, Response, nigeria_grade
from . import db
from sqlalchemy import desc
from xhtml2pdf import pisa
from io import BytesIO


def backfill_session_scores():
    """Backfill scores for existing sessions that don't have stored scores"""
    sessions_to_update = ExamSession.query.filter(
        ExamSession.completed_at.isnot(None),
        (ExamSession.total_questions.is_(None) | 
         ExamSession.correct_answers.is_(None) | 
         ExamSession.score_percentage.is_(None))
    ).all()
    
    for session in sessions_to_update:
        questions = Question.query.filter_by(subject_id=session.subject_id).all()
        total = len(questions)
        correct = 0
        
        for q in questions:
            resp = Response.query.filter_by(session_id=session.id, question_id=q.id).first()
            if resp:
                selected_option = Option.query.get(resp.selected_option_id)
                correct_option = Option.query.filter_by(question_id=q.id, is_correct=True).first()
                if selected_option and correct_option and selected_option.id == correct_option.id:
                    correct += 1
        
        percentage = (correct / total * 100) if total > 0 else 0
        session.total_questions = total
        session.correct_answers = correct
        session.score_percentage = percentage
    
    if sessions_to_update:
        db.session.commit()
        print(f"Backfilled scores for {len(sessions_to_update)} sessions")

student_bp = Blueprint("student", __name__)


def _format_api_options(option_dict):
    """Format API options from dictionary to list format"""
    if not option_dict:
        return []
    
    options = []
    for key, value in option_dict.items():
        if value and key in ['a', 'b', 'c', 'd', 'e']:
            options.append({
                'option': value,
                'answer': False  # Will be set based on answer field
            })
    return options


@student_bp.route("/")
@login_required
def index():
    # For SS2 and SS3 students, show API subjects instead of teacher-created subjects
    if current_user.class_name in ['SS 2', 'SS 3']:
        # Import here to avoid circular imports
        from .api_service import SS2_SS3_SUBJECTS
        
        # Create virtual subjects from API
        api_subjects = []
        for subject_key, subject_name in SS2_SS3_SUBJECTS.items():
            # Create a virtual subject object for API subjects
            api_subject = type('APISubject', (), {
                'id': f'api_{subject_key}_{current_user.class_name.replace(" ", "").lower()}',
                'name': subject_name,
                'description': f'{subject_name} questions from external API for {current_user.class_name}',
                'duration_minutes': 45,  # Default duration for API subjects
                'class_name': current_user.class_name,
                'teacher_id': None,
                'created_at': None,
                'is_api_subject': True,
                'subject_key': subject_key,
                'class_level': current_user.class_name.replace(" ", "").lower()
            })()
            api_subjects.append(api_subject)
        
        # Also include teacher-created subjects for SS2/SS3 or all classes
        teacher_subjects = Subject.query.filter(
            (Subject.class_name == None) | 
            (Subject.class_name == current_user.class_name)
        ).order_by(Subject.created_at.desc()).all()
        
        # Combine API subjects and teacher subjects
        all_subjects = api_subjects + teacher_subjects
        
    elif current_user.class_name:
        # For other classes, show subjects that are either for all classes or specifically for the user's class
        all_subjects = Subject.query.filter(
            (Subject.class_name == None) | (Subject.class_name == current_user.class_name)
        ).order_by(Subject.created_at.desc()).all()
    else:
        # If user has no class assigned, show all teacher-created subjects
        all_subjects = Subject.query.order_by(Subject.created_at.desc()).all()
    
    return render_template("student/index.html", subjects=all_subjects)


@student_bp.route("/external-questions")
@login_required
def external_questions():
    """Display external questions for SS2 and SS3 students"""
    return render_template("student/external_questions.html")


@student_bp.route("/api-subjects/<subject_id>/start")
@login_required
def take_api_exam(subject_id):
    """Start an exam using API questions for SS2/SS3 students"""
    if not current_user.class_name in ['SS 2', 'SS 3']:
        flash("API exams are only available for SS2 and SS3 students", "error")
        return redirect(url_for("student.index"))
    
    # Parse the subject_id to get subject key and class level
    # Format: api_chemistry_ss2
    parts = subject_id.split('_')
    if len(parts) != 3 or parts[0] != 'api':
        flash("Invalid subject", "error")
        return redirect(url_for("student.index"))
    
    subject_key = parts[1]
    class_level = parts[2]
    
    # Import API service
    from .api_service import QuestionsAPIService, SS2_SS3_SUBJECTS
    
    if subject_key not in SS2_SS3_SUBJECTS:
        flash("Subject not available", "error")
        return redirect(url_for("student.index"))
    
    # Fetch questions from API (get 20 questions for a good exam experience)
    api_service = QuestionsAPIService()
    result = api_service.fetch_questions(subject_key, "utme", limit=20)
    
    if not result['success']:
        flash(f"Failed to load questions: {result['error']}", "error")
        return redirect(url_for("student.index"))
    
    # Create a virtual subject for display
    virtual_subject = type('VirtualSubject', (), {
        'id': subject_id,
        'name': SS2_SS3_SUBJECTS[subject_key],
        'description': f'{SS2_SS3_SUBJECTS[subject_key]} questions from external API',
        'duration_minutes': 45,
        'class_name': current_user.class_name,
        'is_api_subject': True
    })()
    
    # Process questions from API response
    questions_data = result['data'].get('data', [])
    questions = []
    
    # Handle multiple questions response (list format)
    if isinstance(questions_data, list):
        # Multiple questions response from /m endpoint
        for q_data in questions_data:
            if isinstance(q_data, dict) and 'question' in q_data:
                virtual_question = type('VirtualQuestion', (), {
                    'id': f'api_{q_data.get("id", "1")}',
                    'text': q_data.get('question', ''),
                    'options': _format_api_options(q_data.get('option', {})),
                    'year': q_data.get('year', ''),
                    'examtype': q_data.get('examtype', ''),
                    'subject': q_data.get('subject', ''),
                    'is_api_question': True
                })()
                questions.append(virtual_question)
    elif isinstance(questions_data, dict) and 'question' in questions_data:
        # Single question response from /q endpoint
        q_data = questions_data
        virtual_question = type('VirtualQuestion', (), {
            'id': f'api_{q_data.get("id", "1")}',
            'text': q_data.get('question', ''),
            'options': _format_api_options(q_data.get('option', {})),
            'year': q_data.get('year', ''),
            'examtype': q_data.get('examtype', ''),
            'subject': q_data.get('subject', ''),
            'is_api_question': True
        })()
        questions.append(virtual_question)
    
    if not questions:
        flash("No questions available for this subject", "error")
        return redirect(url_for("student.index"))
    
    # Create a virtual session for tracking
    virtual_session = type('VirtualSession', (), {
        'id': f'api_session_{subject_id}_{current_user.id}',
        'subject_id': subject_id,
        'student_id': current_user.id,
        'started_at': datetime.utcnow(),
        'is_api_session': True
    })()
    
    return render_template(
        "student/take_api_exam.html",
        subject=virtual_subject,
        questions=questions,
        session=virtual_session,
        end_remaining=45 * 60,  # 45 minutes in seconds
        # Pass the original API payload through the form so grading uses the
        # same questions the student answered (prevents mismatch on re-fetch).
        questions_payload=questions_data
    )


@student_bp.route("/api-subjects/<subject_id>/submit", methods=["POST"])
@login_required
def submit_api_exam(subject_id):
    """Submit an API exam and show results"""
    if not current_user.class_name in ['SS 2', 'SS 3']:
        flash("API exams are only available for SS2 and SS3 students", "error")
        return redirect(url_for("student.index"))
    
    # Parse the subject_id
    parts = subject_id.split('_')
    if len(parts) != 3 or parts[0] != 'api':
        flash("Invalid subject", "error")
        return redirect(url_for("student.index"))
    
    subject_key = parts[1]
    class_level = parts[2]
    
    # Import API service
    from .api_service import QuestionsAPIService, SS2_SS3_SUBJECTS
    
    if subject_key not in SS2_SS3_SUBJECTS:
        flash("Subject not available", "error")
        return redirect(url_for("student.index"))
    
    # Prefer using the questions payload embedded in the submitted form. This
    # ensures we grade the exact questions that were presented to the student
    # (prevents mismatches when the external API returns different content on
    # subsequent fetches). If not present, fall back to fetching from API.
    import json

    questions_payload_json = request.form.get('questions_payload_json')
    questions_data = None
    if questions_payload_json:
        try:
            questions_parsed = json.loads(questions_payload_json)
            # The API payload may nest data under 'data'
            if isinstance(questions_parsed, dict) and 'data' in questions_parsed:
                questions_data = questions_parsed.get('data')
            else:
                questions_data = questions_parsed
        except Exception as e:
            print(f"DEBUG: Failed to parse questions_payload_json: {e}")

    if questions_data is None:
        api_service = QuestionsAPIService()
        result = api_service.fetch_questions(subject_key, "utme", limit=20)
        if not result['success']:
            flash(f"Failed to load questions: {result['error']}", "error")
            return redirect(url_for("student.index"))
        questions_data = result['data'].get('data', [])
    total_questions = 0
    correct_answers = 0
    results = []
    
    current_app.logger.debug("Processing API exam submission for subject %s", subject_key)
    # Avoid dumping full form data (may contain non-encodable characters). Log keys only.
    current_app.logger.debug("Form keys received: %s", list(request.form.keys()))
    current_app.logger.debug("Questions data type: %s, length: %s", type(questions_data), len(questions_data) if hasattr(questions_data, '__len__') else 'N/A')
    
    # Handle multiple questions response (list format)
    if isinstance(questions_data, list):
        # Multiple questions response from /m endpoint
        for q_data in questions_data:
            if isinstance(q_data, dict) and 'question' in q_data:
                total_questions += 1
                question_id = f'api_{q_data.get("id", "1")}'
                form_key = f'question_{question_id}'
                submitted_answer = request.form.get(form_key)
                
                current_app.logger.debug("Question ID: %s, Form key: %s, Submitted answer: %s", question_id, form_key, submitted_answer)
                
                # Find correct answer from API format
                correct_answer_key = q_data.get('answer', '')
                correct_answer = None
                if correct_answer_key and correct_answer_key in q_data.get('option', {}):
                    correct_answer = q_data.get('option', {}).get(correct_answer_key)
                
                current_app.logger.debug("Correct answer key: %s, Correct answer: %s", correct_answer_key, correct_answer)
                
                is_correct = submitted_answer == correct_answer
                if is_correct:
                    correct_answers += 1
                
                results.append({
                    'question': q_data.get('question', ''),
                    'submitted_answer': submitted_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'options': _format_api_options(q_data.get('option', {}))
                })
    elif isinstance(questions_data, dict) and 'question' in questions_data:
        # Single question response from /q endpoint
        q_data = questions_data
        total_questions = 1
        question_id = f'api_{q_data.get("id", "1")}'
        submitted_answer = request.form.get(f'question_{question_id}')
        
        # Find correct answer from API format
        correct_answer_key = q_data.get('answer', '')
        correct_answer = None
        if correct_answer_key and correct_answer_key in q_data.get('option', {}):
            correct_answer = q_data.get('option', {}).get(correct_answer_key)
        
        is_correct = submitted_answer == correct_answer
        if is_correct:
            correct_answers += 1
        
        results.append({
            'question': q_data.get('question', ''),
            'submitted_answer': submitted_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'options': _format_api_options(q_data.get('option', {}))
        })
    
    # Calculate score
    percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Create virtual subject for display
    virtual_subject = type('VirtualSubject', (), {
        'id': subject_id,
        'name': SS2_SS3_SUBJECTS[subject_key],
        'description': f'{SS2_SS3_SUBJECTS[subject_key]} questions from external API',
        'is_api_subject': True
    })()
    
    flash("API exam submitted successfully!", "success")
    
    return render_template(
        "student/api_exam_results.html",
        subject=virtual_subject,
        results=results,
        total_questions=total_questions,
        correct_answers=correct_answers,
        percentage=percentage,
        class_level=class_level.upper()
    )


@student_bp.route("/backfill-scores")
@login_required
def backfill_scores():
    """Backfill scores for existing sessions - accessible to teachers and admins"""
    if not current_user.is_teacher():
        flash("Access denied", "error")
        return redirect(url_for("student.index"))
    
    try:
        backfill_session_scores()
        flash("Scores backfilled successfully!", "success")
    except Exception as e:
        flash(f"Error backfilling scores: {str(e)}", "error")
    
    return redirect(url_for("student.index"))


@student_bp.route("/test-report")
@login_required
def test_report():
    """Simple test route to check report data"""
    subjects = Subject.query.all()
    rows = []
    
    for s in subjects:
        sess = (
            ExamSession.query
            .filter_by(subject_id=s.id, student_id=current_user.id)
            .filter(ExamSession.completed_at.isnot(None))
            .order_by(desc(ExamSession.completed_at))
            .first()
        )
        if sess:
            rows.append({
                "subject_name": s.name,
                "session_id": sess.id,
                "completed_at": sess.completed_at,
                "total": sess.total_questions or 0,
                "correct": sess.correct_answers or 0,
                "percentage": sess.score_percentage or 0,
                "grade": nigeria_grade(sess.score_percentage or 0)
            })
    
    return f"""
    <h1>Test Report Data</h1>
    <p>User: {current_user.full_name}</p>
    <p>Total subjects: {len(subjects)}</p>
    <p>Rows found: {len(rows)}</p>
    <pre>{rows}</pre>
    """


@student_bp.route("/create-test-session")
@login_required
def create_test_session():
    """Create a test exam session for debugging"""
    if not current_user.is_teacher():
        flash("Access denied", "error")
        return redirect(url_for("student.index"))
    
    # Find a subject with questions
    subjects = Subject.query.all()
    test_subject = None
    for subject in subjects:
        questions = Question.query.filter_by(subject_id=subject.id).all()
        if questions:
            test_subject = subject
            break
    
    if not test_subject:
        flash("No subjects with questions found", "error")
        return redirect(url_for("student.index"))
    
    # Create a test session for the current user
    session = ExamSession(
        subject_id=test_subject.id,
        student_id=current_user.id,
        started_at=datetime.utcnow()
    )
    db.session.add(session)
    db.session.commit()
    
    flash(f"Created test session {session.id} for subject '{test_subject.name}'", "success")
    return redirect(url_for("student.take_exam", session_id=session.id))


@student_bp.route("/test-complete-session/<int:session_id>")
@login_required
def test_complete_session(session_id):
    """Manually complete a session for testing (teachers only)"""
    if not current_user.is_teacher():
        flash("Access denied", "error")
        return redirect(url_for("student.index"))
    
    session = ExamSession.query.get_or_404(session_id)
    
    # Create some dummy responses
    questions = Question.query.filter_by(subject_id=session.subject_id).all()
    for question in questions:
        # Find the first option for each question
        first_option = Option.query.filter_by(question_id=question.id).first()
        if first_option:
            # Check if response already exists
            existing_response = Response.query.filter_by(session_id=session.id, question_id=question.id).first()
            if not existing_response:
                response = Response(
                    session_id=session.id,
                    question_id=question.id,
                    selected_option_id=first_option.id
                )
                db.session.add(response)
    
    # Calculate and store scores
    total_questions = len(questions)
    correct_answers = 0
    
    for question in questions:
        response = Response.query.filter_by(session_id=session.id, question_id=question.id).first()
        if response:
            selected_option = Option.query.get(response.selected_option_id)
            correct_option = Option.query.filter_by(question_id=question.id, is_correct=True).first()
            if selected_option and correct_option and selected_option.id == correct_option.id:
                correct_answers += 1
    
    percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Mark session as completed
    session.completed_at = datetime.utcnow()
    session.total_questions = total_questions
    session.correct_answers = correct_answers
    session.score_percentage = percentage
    
    db.session.commit()
    
    flash(f"Session {session_id} completed manually. Scores: {correct_answers}/{total_questions} ({percentage:.1f}%)", "success")
    return redirect(url_for("student.full_diagnostic"))


@student_bp.route("/full-diagnostic")
@login_required
def full_diagnostic():
    """Comprehensive diagnostic of the entire CBT system"""
    diagnostic_info = {
        'current_user': {
            'name': current_user.full_name,
            'id': current_user.id,
            'role': current_user.role,
            'class': current_user.class_name
        },
        'database_stats': {
            'total_users': User.query.count(),
            'total_subjects': Subject.query.count(),
            'total_questions': Question.query.count(),
            'total_sessions': ExamSession.query.count(),
            'total_responses': Response.query.count(),
            'completed_sessions': ExamSession.query.filter(ExamSession.completed_at.isnot(None)).count()
        },
        'user_sessions': [],
        'user_responses': [],
        'subjects_with_questions': [],
        'report_card_data': []
    }
    
    # Get all sessions for current user
    user_sessions = ExamSession.query.filter_by(student_id=current_user.id).all()
    for session in user_sessions:
        subject = Subject.query.get(session.subject_id)
        diagnostic_info['user_sessions'].append({
            'id': session.id,
            'subject_name': subject.name if subject else 'Unknown',
            'subject_id': session.subject_id,
            'started_at': session.started_at,
            'completed_at': session.completed_at,
            'total_questions': session.total_questions,
            'correct_answers': session.correct_answers,
            'score_percentage': session.score_percentage,
            'is_completed': session.completed_at is not None,
            'has_scores': session.total_questions is not None and session.correct_answers is not None and session.score_percentage is not None
        })
    
    # Get all responses for current user's sessions
    for session in user_sessions:
        responses = Response.query.filter_by(session_id=session.id).all()
        for response in responses:
            question = Question.query.get(response.question_id)
            selected_option = Option.query.get(response.selected_option_id)
            correct_option = Option.query.filter_by(question_id=response.question_id, is_correct=True).first()
            
            diagnostic_info['user_responses'].append({
                'session_id': session.id,
                'question_id': response.question_id,
                'question_text': question.text if question else 'Unknown',
                'selected_option_id': response.selected_option_id,
                'selected_option_text': selected_option.text if selected_option else 'Unknown',
                'correct_option_id': correct_option.id if correct_option else None,
                'correct_option_text': correct_option.text if correct_option else 'Unknown',
                'is_correct': selected_option and correct_option and selected_option.id == correct_option.id
            })
    
    # Get subjects with questions
    subjects = Subject.query.all()
    for subject in subjects:
        questions = Question.query.filter_by(subject_id=subject.id).all()
        questions_info = []
        for question in questions:
            options = Option.query.filter_by(question_id=question.id).all()
            correct_options = Option.query.filter_by(question_id=question.id, is_correct=True).all()
            questions_info.append({
                'id': question.id,
                'text': question.text,
                'options_count': len(options),
                'correct_options_count': len(correct_options),
                'options': [{'id': opt.id, 'text': opt.text, 'is_correct': opt.is_correct} for opt in options]
            })
        
        diagnostic_info['subjects_with_questions'].append({
            'id': subject.id,
            'name': subject.name,
            'questions_count': len(questions),
            'questions': questions_info
        })
    
    # Test report card logic
    subjects = Subject.query.all()
    rows = []
    for s in subjects:
        sess = (
            ExamSession.query
            .filter_by(subject_id=s.id, student_id=current_user.id)
            .filter(ExamSession.completed_at.isnot(None))
            .order_by(desc(ExamSession.completed_at))
            .first()
        )
        if sess:
            # Use stored scores if available, otherwise calculate
            if sess.total_questions is not None and sess.correct_answers is not None and sess.score_percentage is not None:
                total = sess.total_questions
                correct = sess.correct_answers
                percentage = sess.score_percentage
            else:
                # Fallback: calculate scores
                questions = Question.query.filter_by(subject_id=s.id).all()
                total = len(questions)
                correct = 0
                for q in questions:
                    resp = Response.query.filter_by(session_id=sess.id, question_id=q.id).first()
                    sel = Option.query.get(resp.selected_option_id) if resp else None
                    ans = Option.query.filter_by(question_id=q.id, is_correct=True).first()
                    if sel and ans and sel.id == ans.id:
                        correct += 1
                percentage = (correct / total * 100) if total else 0
            
            grade = nigeria_grade(percentage)
            rows.append({
                "subject_name": s.name,
                "session_id": sess.id,
                "completed_at": sess.completed_at,
                "total": total,
                "correct": correct,
                "percentage": percentage,
                "grade": grade,
                "has_stored_scores": sess.total_questions is not None
            })
    
    diagnostic_info['report_card_data'] = rows
    
    return render_template("full_diagnostic.html", diagnostic_info=diagnostic_info)


@student_bp.route("/debug-report")
@login_required
def debug_report():
    """Debug route to check why report card shows no sessions"""
    debug_info = {
        'current_user': current_user.full_name,
        'user_id': current_user.id,
        'user_role': current_user.role,
        'total_subjects': Subject.query.count(),
        'total_sessions': ExamSession.query.count(),
        'user_sessions': ExamSession.query.filter_by(student_id=current_user.id).count(),
        'completed_sessions': ExamSession.query.filter_by(student_id=current_user.id).filter(ExamSession.completed_at.isnot(None)).count(),
    }
    
    # Get detailed session info
    sessions = ExamSession.query.filter_by(student_id=current_user.id).all()
    debug_info['sessions_detail'] = []
    for session in sessions:
        debug_info['sessions_detail'].append({
            'id': session.id,
            'subject_id': session.subject_id,
            'started_at': session.started_at,
            'completed_at': session.completed_at,
            'total_questions': session.total_questions,
            'correct_answers': session.correct_answers,
            'score_percentage': session.score_percentage,
        })
    
    # Test the report card logic
    subjects = Subject.query.all()
    report_rows = []
    for s in subjects:
        sess = (
            ExamSession.query
            .filter_by(subject_id=s.id, student_id=current_user.id)
            .filter(ExamSession.completed_at.isnot(None))
            .order_by(desc(ExamSession.completed_at))
            .first()
        )
        if sess:
            report_rows.append({
                'subject_name': s.name,
                'session_id': sess.id,
                'completed_at': sess.completed_at,
                'has_scores': sess.total_questions is not None and sess.correct_answers is not None and sess.score_percentage is not None
            })
    
    debug_info['report_rows'] = report_rows
    debug_info['report_rows_count'] = len(report_rows)
    
    return render_template("debug_report.html", debug_info=debug_info)


@student_bp.route("/report-card")
@login_required
def report_card():
    # Auto-backfill scores for existing sessions if needed
    try:
        backfill_session_scores()
    except Exception as e:
        print(f"Auto-backfill failed: {e}")
    
    # Latest completed session per subject for current user
    subjects = Subject.query.all()
    rows = []
    total_scores = []
    
    print(f"DEBUG: Generating report for user {current_user.full_name} (ID: {current_user.id})")
    print(f"DEBUG: Found {len(subjects)} subjects")
    
    for s in subjects:
        sess = (
            ExamSession.query
            .filter_by(subject_id=s.id, student_id=current_user.id)
            .filter(ExamSession.completed_at.isnot(None))
            .order_by(desc(ExamSession.completed_at))
            .first()
        )
        if not sess:
            continue
        
        # Use stored scores if available, otherwise calculate
        if sess.total_questions is not None and sess.correct_answers is not None and sess.score_percentage is not None:
            total = sess.total_questions
            correct = sess.correct_answers
            percentage = sess.score_percentage
        else:
            # Fallback: calculate scores (for old sessions)
            questions = Question.query.filter_by(subject_id=s.id).all()
            total = len(questions)
            correct = 0
            for q in questions:
                resp = Response.query.filter_by(session_id=sess.id, question_id=q.id).first()
                sel = Option.query.get(resp.selected_option_id) if resp else None
                ans = Option.query.filter_by(question_id=q.id, is_correct=True).first()
                if sel and ans and sel.id == ans.id:
                    correct += 1
            percentage = (correct / total * 100) if total else 0
        
        grade = nigeria_grade(percentage)
        rows.append({
            "subject": s,
            "session": sess,
            "total": total,
            "correct": correct,
            "percentage": percentage,
            "grade": grade,
        })
        total_scores.append(percentage)
    overall = sum(total_scores) / len(total_scores) if total_scores else 0
    overall_grade = nigeria_grade(overall)
    return render_template("student/report_card.html", rows=rows, overall=overall, overall_grade=overall_grade)


@student_bp.route("/report-card.pdf")
@login_required
def report_card_pdf():
    # Auto-backfill scores for existing sessions if needed
    try:
        backfill_session_scores()
    except Exception as e:
        print(f"Auto-backfill failed: {e}")
    
    # Get the same data as the report_card function
    subjects = Subject.query.all()
    rows = []
    total_scores = []
    for s in subjects:
        sess = (
            ExamSession.query
            .filter_by(subject_id=s.id, student_id=current_user.id)
            .filter(ExamSession.completed_at.isnot(None))
            .order_by(desc(ExamSession.completed_at))
            .first()
        )
        if not sess:
            continue
        
        # Use stored scores if available, otherwise calculate
        if sess.total_questions is not None and sess.correct_answers is not None and sess.score_percentage is not None:
            total = sess.total_questions
            correct = sess.correct_answers
            percentage = sess.score_percentage
        else:
            # Fallback: calculate scores (for old sessions)
            questions = Question.query.filter_by(subject_id=s.id).all()
            total = len(questions)
            correct = 0
            for q in questions:
                resp = Response.query.filter_by(session_id=sess.id, question_id=q.id).first()
                sel = Option.query.get(resp.selected_option_id) if resp else None
                ans = Option.query.filter_by(question_id=q.id, is_correct=True).first()
                if sel and ans and sel.id == ans.id:
                    correct += 1
            percentage = (correct / total * 100) if total else 0
        
        grade = nigeria_grade(percentage)
        rows.append({
            "subject": s,
            "session": sess,
            "total": total,
            "correct": correct,
            "percentage": percentage,
            "grade": grade,
        })
        total_scores.append(percentage)
    overall = sum(total_scores) / len(total_scores) if total_scores else 0
    overall_grade = nigeria_grade(overall)
    
    html = render_template("student/report_card_pdf.html", user=current_user, rows=rows, overall=overall, overall_grade=overall_grade)
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=pdf)
    if pisa_status.err:
        flash("Failed to generate PDF", "error")
        return redirect(url_for("student.report_card"))
    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report_card.pdf'
    return response


@student_bp.route("/subjects/<subject_id>/start")
@login_required
def start_exam(subject_id):
    # Check if this is an API subject
    if subject_id.startswith('api_'):
        # Handle API subject
        return redirect(url_for("student.take_api_exam", subject_id=subject_id))
    
    # Handle regular teacher-created subject
    subject = Subject.query.get_or_404(subject_id)
    existing = ExamSession.query.filter_by(subject_id=subject.id, student_id=current_user.id, completed_at=None).order_by(ExamSession.started_at.desc()).first()
    now = datetime.utcnow()
    new_session_needed = True
    if existing:
        end_time = existing.started_at + timedelta(minutes=subject.duration_minutes)
        if end_time > now:
            session = existing
            new_session_needed = False
    if new_session_needed:
        session = ExamSession(subject_id=subject.id, student_id=current_user.id, started_at=now)
        db.session.add(session)
        db.session.commit()
    return redirect(url_for("student.take_exam", session_id=session.id))


@student_bp.route("/sessions/<int:session_id>", methods=["GET", "POST"])
@login_required
def take_exam(session_id):
    session = ExamSession.query.get_or_404(session_id)
    if session.student_id != current_user.id:
        flash("Not authorized", "error")
        return redirect(url_for("student.index"))
    subject = Subject.query.get(session.subject_id)
    questions = Question.query.filter_by(subject_id=subject.id).all()

    if request.method == "POST":
        print(f"DEBUG: Processing exam submission for session {session.id}")
        
        # Process all responses
        responses_processed = 0
        for q in questions:
            key = f"question_{q.id}"
            selected_option_id = request.form.get(key)
            print(f"DEBUG: Question {q.id} - Form key: {key}, Selected option: {selected_option_id}")
            if not selected_option_id:
                print(f"DEBUG: No answer provided for question {q.id}")
                continue
            
            existing_resp = Response.query.filter_by(session_id=session.id, question_id=q.id).first()
            if existing_resp:
                existing_resp.selected_option_id = int(selected_option_id)
                print(f"DEBUG: Updated existing response for question {q.id}")
            else:
                db.session.add(Response(session_id=session.id, question_id=q.id, selected_option_id=int(selected_option_id)))
                print(f"DEBUG: Created new response for question {q.id}")
            responses_processed += 1
        
        print(f"DEBUG: Processed {responses_processed} responses out of {len(questions)} questions")
        
        # Calculate and store the score
        total_questions = len(questions)
        correct_answers = 0
        
        print(f"DEBUG: Starting score calculation for {total_questions} questions")
        for q in questions:
            resp = Response.query.filter_by(session_id=session.id, question_id=q.id).first()
            if resp:
                selected_option = Option.query.get(resp.selected_option_id)
                correct_option = Option.query.filter_by(question_id=q.id, is_correct=True).first()
                
                print(f"DEBUG: Q{q.id} - Selected: {selected_option.text if selected_option else 'None'}, Correct: {correct_option.text if correct_option else 'None'}")
                
                if selected_option and correct_option and selected_option.id == correct_option.id:
                    correct_answers += 1
                    print(f"DEBUG: Q{q.id} - CORRECT")
                else:
                    print(f"DEBUG: Q{q.id} - WRONG")
            else:
                print(f"DEBUG: Q{q.id} - No response found")
        
        # Store the score in the session
        percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        session.completed_at = datetime.utcnow()
        session.total_questions = total_questions
        session.correct_answers = correct_answers
        session.score_percentage = percentage
        
        print(f"DEBUG: Final scores - Total: {total_questions}, Correct: {correct_answers}, Percentage: {percentage}%")
        print(f"DEBUG: Session completed_at set to: {session.completed_at}")
        
        db.session.commit()
        print(f"DEBUG: Scores saved to database successfully")
        
        flash("Exam submitted successfully!", "success")
        return redirect(url_for("report.session_report", session_id=session.id))

    # Compute remaining seconds server-side to avoid client clock skew
    now = datetime.utcnow()
    end_time = session.started_at + timedelta(minutes=subject.duration_minutes)
    remaining_seconds = max(0, int((end_time - now).total_seconds()))

    # If session expired but no answers yet, reset start time and recompute
    if remaining_seconds == 0:
        has_answers = db.session.query(Response.id).filter_by(session_id=session.id).first() is not None
        if not has_answers:
            session.started_at = now
            db.session.commit()
            end_time = session.started_at + timedelta(minutes=subject.duration_minutes)
            remaining_seconds = max(0, int((end_time - datetime.utcnow()).total_seconds()))

    return render_template(
        "student/take_exam.html",
        subject=subject,
        questions=questions,
        session=session,
        end_remaining=remaining_seconds,
    )
