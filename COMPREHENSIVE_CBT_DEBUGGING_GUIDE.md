# Comprehensive CBT Debugging Guide

## Problem Summary
The report card is showing no calculations or records, indicating that either:
1. No exam sessions are being created
2. Exam sessions are created but not marked as completed
3. Scores are not being calculated or stored properly
4. The report card logic is not finding the completed sessions

## Debug Tools Implemented

### 1. Full Diagnostic Route
**URL**: `/student/full-diagnostic`
**Purpose**: Comprehensive analysis of the entire CBT system
**Shows**:
- Current user information
- Database statistics (users, subjects, questions, sessions, responses)
- All exam sessions for the current user with completion status
- All exam responses with correct/incorrect status
- Subjects and their questions with validation
- Report card data that would be generated

### 2. Simple Test Route
**URL**: `/student/test-report`
**Purpose**: Quick check of report card data
**Shows**: Raw data that would be displayed in the report card

### 3. Create Test Session Route
**URL**: `/student/create-test-session` (Teachers only)
**Purpose**: Create a test exam session for debugging
**Action**: Creates a new exam session that can be used for testing

### 4. Enhanced Exam Submission Logging
**Added**: Detailed debug logging in the `take_exam` function
**Shows**: 
- Each question and selected answer
- Score calculation process
- Database save operations

## How to Use These Tools

### Step 1: Check Current State
1. Visit `/student/full-diagnostic` to see the complete system state
2. Look for:
   - Are there any exam sessions?
   - Are any sessions marked as completed?
   - Do completed sessions have scores?
   - Are there any exam responses?

### Step 2: Test Exam Flow
1. **If no sessions exist**: Create a test session using `/student/create-test-session`
2. **Take an exam**: Go through the complete exam process
3. **Submit the exam**: Watch the console/logs for debug output
4. **Check results**: Visit `/student/full-diagnostic` again to see if scores were saved

### Step 3: Verify Report Card Logic
1. Visit `/student/test-report` to see raw report data
2. Compare with `/student/report-card` to see if they match

## Common Issues and Solutions

### Issue 1: No Exam Sessions Found
**Symptoms**: Full diagnostic shows 0 exam sessions
**Solutions**:
- Check if students are actually starting exams
- Verify the exam start process works
- Check if there are subjects with questions

### Issue 2: Sessions Not Completed
**Symptoms**: Sessions exist but `completed_at` is NULL
**Solutions**:
- Check if students are submitting exams properly
- Verify the form submission process
- Check browser console for JavaScript errors

### Issue 3: Scores Not Calculated
**Symptoms**: Sessions are completed but scores are NULL
**Solutions**:
- Check the exam submission debug logs
- Verify questions have correct answers set
- Check if responses are being saved properly

### Issue 4: Report Card Logic Issues
**Symptoms**: Data exists but report card is empty
**Solutions**:
- Check the report card query logic
- Verify user permissions and session ownership
- Check for database query errors

## Expected Debug Output

When an exam is submitted, you should see output like:
```
DEBUG: Processing exam submission for session 123
DEBUG: Question 1 - Form key: question_1, Selected option: 5
DEBUG: Question 2 - Form key: question_2, Selected option: 8
DEBUG: Processed 2 responses out of 2 questions
DEBUG: Starting score calculation for 2 questions
DEBUG: Q1 - Selected: Option A, Correct: Option A
DEBUG: Q1 - CORRECT
DEBUG: Q2 - Selected: Option B, Correct: Option C
DEBUG: Q2 - WRONG
DEBUG: Final scores - Total: 2, Correct: 1, Percentage: 50.0%
DEBUG: Session completed_at set to: 2024-01-15 10:30:00
DEBUG: Scores saved to database successfully
```

## Quick Fixes to Try

### Fix 1: Manual Backfill
If you have completed sessions without scores:
1. Visit `/student/backfill-scores` (teachers only)
2. This will calculate and store scores for existing sessions

### Fix 2: Check Questions
Ensure questions have correct answers set:
1. Go to teacher dashboard
2. Edit each question
3. Make sure one option is marked as correct

### Fix 3: Test with New Session
1. Create a test session using `/student/create-test-session`
2. Take the exam and submit it
3. Check if scores are calculated and stored

## Next Steps

1. **Run the diagnostic**: Visit `/student/full-diagnostic` to see current state
2. **Identify the issue**: Based on diagnostic results, determine what's missing
3. **Test the flow**: Create a test session and go through the complete exam process
4. **Check logs**: Look for debug output during exam submission
5. **Verify results**: Check if scores are properly calculated and stored

The debug tools will show you exactly where the problem is in the CBT system. Once you identify the issue using these tools, we can implement the appropriate fix.
