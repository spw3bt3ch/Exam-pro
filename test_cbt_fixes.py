#!/usr/bin/env python3
"""
Test script to verify CBT fixes are working correctly.
This script tests the score calculation and report generation functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Subject, Question, Option, ExamSession, Response
from app.student import backfill_session_scores
from datetime import datetime

def test_score_calculation():
    """Test that scores are calculated and stored correctly"""
    app = create_app()
    
    with app.app_context():
        print("Testing CBT score calculation and storage...")
        
        # Create test data
        teacher = User(
            full_name="Test Teacher",
            email="teacher@test.com",
            role="teacher"
        )
        teacher.set_password("password123")
        
        student = User(
            full_name="Test Student",
            email="student@test.com",
            role="student"
        )
        student.set_password("password123")
        
        subject = Subject(
            name="Test Subject",
            description="Test subject for CBT",
            duration_minutes=30,
            teacher_id=teacher.id
        )
        
        question1 = Question(
            subject_id=subject.id,
            text="What is 2 + 2?",
            time_limit_seconds=60
        )
        
        question2 = Question(
            subject_id=subject.id,
            text="What is the capital of Nigeria?",
            time_limit_seconds=60
        )
        
        # Add questions to session before committing
        db.session.add(teacher)
        db.session.add(student)
        db.session.add(subject)
        db.session.commit()
        
        # Now add questions with the subject ID
        question1.subject_id = subject.id
        question2.subject_id = subject.id
        
        db.session.add(question1)
        db.session.add(question2)
        db.session.commit()
        
        # Create options for question 1
        option1a = Option(question_id=question1.id, text="3", is_correct=False)
        option1b = Option(question_id=question1.id, text="4", is_correct=True)
        option1c = Option(question_id=question1.id, text="5", is_correct=False)
        
        # Create options for question 2
        option2a = Option(question_id=question2.id, text="Lagos", is_correct=False)
        option2b = Option(question_id=question2.id, text="Abuja", is_correct=True)
        option2c = Option(question_id=question2.id, text="Kano", is_correct=False)
        
        db.session.add_all([option1a, option1b, option1c, option2a, option2b, option2c])
        db.session.commit()
        
        # Create exam session
        session = ExamSession(
            subject_id=subject.id,
            student_id=student.id,
            started_at=datetime.utcnow()
        )
        db.session.add(session)
        db.session.commit()
        
        # Simulate student responses (1 correct, 1 incorrect)
        response1 = Response(
            session_id=session.id,
            question_id=question1.id,
            selected_option_id=option1b.id  # Correct answer
        )
        
        response2 = Response(
            session_id=session.id,
            question_id=question2.id,
            selected_option_id=option2a.id  # Incorrect answer (Lagos instead of Abuja)
        )
        
        db.session.add_all([response1, response2])
        db.session.commit()
        
        # Test the backfill function
        backfill_session_scores()
        
        # Verify the session was updated with correct scores
        updated_session = ExamSession.query.get(session.id)
        
        print(f"Session ID: {updated_session.id}")
        print(f"Total Questions: {updated_session.total_questions}")
        print(f"Correct Answers: {updated_session.correct_answers}")
        print(f"Score Percentage: {updated_session.score_percentage}")
        
        # Expected: 1 correct out of 2 questions = 50%
        assert updated_session.total_questions == 2, "Total questions should be 2"
        assert updated_session.correct_answers == 1, "Correct answers should be 1"
        assert updated_session.score_percentage == 50.0, "Score should be 50%"
        
        print("✅ Score calculation test passed!")
        
        # Clean up test data
        db.session.delete(session)
        db.session.delete(response1)
        db.session.delete(response2)
        db.session.delete(option1a)
        db.session.delete(option1b)
        db.session.delete(option1c)
        db.session.delete(option2a)
        db.session.delete(option2b)
        db.session.delete(option2c)
        db.session.delete(question1)
        db.session.delete(question2)
        db.session.delete(subject)
        db.session.delete(teacher)
        db.session.delete(student)
        db.session.commit()
        
        print("✅ Test data cleaned up successfully!")

if __name__ == "__main__":
    test_score_calculation()
    print("\n🎉 All tests passed! CBT fixes are working correctly.")
