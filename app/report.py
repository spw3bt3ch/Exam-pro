from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import ExamSession, Question, Option, Response, nigeria_grade

report_bp = Blueprint("report", __name__)


@report_bp.route("/session/<int:session_id>")
@login_required
def session_report(session_id):
    session = ExamSession.query.get_or_404(session_id)
    if session.student_id != current_user.id and not current_user.is_teacher():
        return render_template("errors/403.html"), 403

    questions = Question.query.filter_by(subject_id=session.subject_id).all()
    details = []

    # Use stored scores if available, otherwise calculate
    if session.total_questions is not None and session.correct_answers is not None and session.score_percentage is not None:
        total = session.total_questions
        correct = session.correct_answers
        percentage = session.score_percentage
    else:
        # Fallback: calculate scores (for old sessions)
        total = len(questions)
        correct = 0
        
        for q in questions:
            resp = Response.query.filter_by(session_id=session.id, question_id=q.id).first()
            selected = Option.query.get(resp.selected_option_id) if resp else None
            correct_option = Option.query.filter_by(question_id=q.id, is_correct=True).first()
            is_correct = selected and selected.id == (correct_option.id if correct_option else None)
            correct += 1 if is_correct else 0
        
        percentage = (correct / total * 100) if total else 0

    # Get detailed results for display
    for q in questions:
        resp = Response.query.filter_by(session_id=session.id, question_id=q.id).first()
        selected = Option.query.get(resp.selected_option_id) if resp else None
        correct_option = Option.query.filter_by(question_id=q.id, is_correct=True).first()
        is_correct = selected and selected.id == (correct_option.id if correct_option else None)
        details.append({
            "question": q,
            "selected": selected,
            "correct_option": correct_option,
            "is_correct": is_correct,
        })

    grade = nigeria_grade(percentage)

    return render_template("report/session.html", session=session, details=details, total=total, correct=correct, percentage=percentage, grade=grade)
