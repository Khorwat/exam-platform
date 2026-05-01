from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from .models import ExamSession, ExamAnswer
from .serializers import (
    ExamSessionSerializer, ExamAnswerSerializer,
    StartExamSessionSerializer, SubmitAnswerSerializer
)
from .security import check_rate_limit, validate_exam_access, log_suspicious_activity
from questions.serializers import QuestionSerializer, QuestionOptionSerializer
from exams.models import Exam, ExamQuestion
from accounts.permissions import IsStudent
import random


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_exam(request):
    """Start an exam session for a student"""
    serializer = StartExamSessionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    exam_id = serializer.validated_data['exam_id']
    
    # Rate limiting
    if not check_rate_limit(request.user.id, 'start_exam', limit=5, window=300):
        return Response({'error': 'Too many exam start attempts. Please try again later.'}, 
                       status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    try:
        exam = Exam.objects.get(id=exam_id, is_active=True)
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found or not active'}, status=status.HTTP_404_NOT_FOUND)
    
    # Validate exam access
    access, message = validate_exam_access(request.user, exam)
    if not access:
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if student already has an active session
    active_session = ExamSession.objects.filter(
        exam=exam,
        student=request.user,
        status='in_progress'
    ).first()
    
    if active_session:
        # Check time limit
        if active_session.check_time_limit():
            return Response({'error': 'Previous session expired'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ExamSessionSerializer(active_session).data)
    
    # Check if retake is allowed
    if not exam.allow_retake:
        existing_session = ExamSession.objects.filter(
            exam=exam,
            student=request.user,
            status__in=['submitted', 'time_up']
        ).exists()
        if existing_session:
            return Response({'error': 'You have already taken this exam'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create new session
    with transaction.atomic():
        session = ExamSession.objects.create(
            exam=exam,
            student=request.user,
            status='in_progress',
            ip_address=request.META.get('REMOTE_ADDR'),
            time_remaining_seconds=exam.duration_minutes * 60
        )
        
        # Get questions for this exam
        exam_questions = ExamQuestion.objects.filter(exam=exam).select_related('question')
        question_list = list(exam_questions)
        
        # Randomize if enabled
        if exam.randomize_questions:
            random.shuffle(question_list)
        
        # Create answer placeholders (not required, but can be done)
        # Answers will be created when student submits them
    
    # Prepare questions with options
    questions_data = []
    # We already have question_list from above
    
    # Get questions for this exam
    # Already fetched in exam_questions/question_list
    
    for eq in question_list:
        question = eq.question
        question_data = QuestionSerializer(question).data
        
        # Randomize options if enabled
        if exam.randomize_options and question.question_type in ['multiple_choice', 'true_false']:
            options = list(question.options.all())
            random.shuffle(options)
            question_data['options'] = QuestionOptionSerializer(options, many=True).data
        else:
            question_data['options'] = QuestionOptionSerializer(question.options.all(), many=True).data
            
        questions_data.append(question_data)
    
    response_data = ExamSessionSerializer(session).data
    response_data['questions'] = questions_data
    
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exam_session(request, session_id):
    """Get exam session details with questions"""
    try:
        if request.user.is_instructor or request.user.is_administrator:
            # Instructors can view any session
            session = ExamSession.objects.get(id=session_id)
        else:
            # Students can only view their own session
            session = ExamSession.objects.get(id=session_id, student=request.user)
    except ExamSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check time limit
    if session.is_active:
        session.check_time_limit()
        session.refresh_from_db()
    
    # Get questions for this exam
    exam_questions = ExamQuestion.objects.filter(exam=session.exam).select_related('question')
    question_list = list(exam_questions)
    
    # Randomize if enabled
    if session.exam.randomize_questions:
        random.shuffle(question_list)
    
    # Get existing answers
    existing_answers = {ans.question_id: ans for ans in session.answers.all()}
    
    # Prepare questions with options
    questions_data = []
    for eq in question_list:
        question = eq.question
        question_data = QuestionSerializer(question).data
        
        # Randomize options if enabled
        if session.exam.randomize_options and question.question_type in ['multiple_choice', 'true_false']:
            options = list(question.options.all())
            random.shuffle(options)
            question_data['options'] = QuestionOptionSerializer(options, many=True).data
        else:
            question_data['options'] = QuestionOptionSerializer(question.options.all(), many=True).data
        
        # Add existing answer if any
        if question.id in existing_answers:
            answer = existing_answers[question.id]
            question_data['answer'] = ExamAnswerSerializer(answer).data
        
        questions_data.append(question_data)
    
    response_data = ExamSessionSerializer(session).data
    response_data['questions'] = questions_data
    response_data['time_remaining'] = max(0, (session.exam.duration_minutes * 60) - session.time_elapsed_seconds)
    
    return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request, session_id):
    """Submit an answer for a question"""
    # Rate limiting for answer submission
    if not check_rate_limit(request.user.id, 'submit_answer', limit=100, window=60):
        log_suspicious_activity(request.user.id, None, 'rate_limit_exceeded', 
                               {'action': 'submit_answer', 'session_id': session_id})
        return Response({'error': 'Too many submissions. Please slow down.'}, 
                       status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    try:
        session = ExamSession.objects.get(id=session_id, student=request.user, status='in_progress')
    except ExamSession.DoesNotExist:
        return Response({'error': 'Active session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check time limit
    if session.check_time_limit():
        return Response({'error': 'Time limit exceeded'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check IP address (security check)
    current_ip = request.META.get('REMOTE_ADDR')
    if session.ip_address and session.ip_address != current_ip:
        log_suspicious_activity(request.user.id, session.exam.id, 'ip_change', 
                               {'old_ip': session.ip_address, 'new_ip': current_ip})
    
    serializer = SubmitAnswerSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    question_id = serializer.validated_data['question_id']
    selected_option_id = serializer.validated_data.get('selected_option_id')
    
    try:
        from questions.models import Question
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if question belongs to this exam
    if not ExamQuestion.objects.filter(exam=session.exam, question=question).exists():
        return Response({'error': 'Question does not belong to this exam'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create or update answer
    answer, created = ExamAnswer.objects.get_or_create(
        session=session,
        question=question,
        defaults={
            'selected_option_id': selected_option_id,
        }
    )
    
    if not created:
        if selected_option_id is not None:
            answer.selected_option_id = selected_option_id
        answer.save()
    
    answer.calculate_score()
    
    return Response(ExamAnswerSerializer(answer).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_exam(request, session_id):
    """Submit the entire exam"""
    try:
        session = ExamSession.objects.get(id=session_id, student=request.user, status='in_progress')
    except ExamSession.DoesNotExist:
        return Response({'error': 'Active session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    session.submit()
    
    # Calculate total score and create result
    from results.models import ExamResult, PerformanceAnalytics
    
    # Create or update result
    result, created = ExamResult.objects.get_or_create(session=session)
    result.calculate_score()
    
    # Update analytics
    analytics, _ = PerformanceAnalytics.objects.get_or_create(
        exam=session.exam,
        student=request.user
    )
    analytics.update_analytics()
    
    return Response({
        'message': 'Exam submitted successfully',
        'total_points': result.total_points_earned,
        'max_points': result.total_points_possible,
        'percentage': result.percentage_score,
        'passed': result.passed,
        'session': ExamSessionSerializer(session).data
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_activity(request, session_id):
    """Log suspicious activity from frontend"""
    try:
        session = ExamSession.objects.get(id=session_id, student=request.user)
    except ExamSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    activity_type = request.data.get('type')
    details = request.data.get('details', {})
    
    log_suspicious_activity(
        user_id=request.user.id,
        exam_id=session.exam.id,
        activity_type=activity_type,
        details=details
    )
    
    return Response({'status': 'logged'})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_answer_score(request, session_id, answer_id):
    """Update score for a specific answer (Manual Grading)"""
    # Check permissions (Instructor or Admin)
    if not (request.user.is_instructor or request.user.is_administrator):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        session = ExamSession.objects.get(id=session_id)
        answer = ExamAnswer.objects.get(id=answer_id, session=session)
    except (ExamSession.DoesNotExist, ExamAnswer.DoesNotExist):
        return Response({'error': 'Session or Answer not found'}, status=status.HTTP_404_NOT_FOUND)
    
    points = request.data.get('points')
    is_correct = request.data.get('is_correct')
    
    if points is not None:
        try:
            answer.points_earned = float(points)
        except ValueError:
            return Response({'error': 'Invalid points value'}, status=status.HTTP_400_BAD_REQUEST)
            
    if is_correct is not None:
        answer.is_correct = is_correct
        
    answer.save()
    
    # Recalculate session score if result exists
    if hasattr(session, 'result'):
        session.result.calculate_score()
        
    return Response(ExamAnswerSerializer(answer).data)


class ExamSessionListView(generics.ListAPIView):
    """List all exam sessions for the current user"""
    serializer_class = ExamSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            return ExamSession.objects.filter(student=user)
        elif user.is_instructor or user.is_administrator:
            exam_id = self.request.query_params.get('exam_id')
            queryset = ExamSession.objects.all()
            if exam_id:
                queryset = queryset.filter(exam_id=exam_id)
            return queryset
        return ExamSession.objects.none()

