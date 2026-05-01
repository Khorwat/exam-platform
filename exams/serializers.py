from rest_framework import serializers
from .models import Exam, ExamQuestion, ExamSchedule
from questions.serializers import QuestionSerializer
from django.utils import timezone


class ExamQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    question_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ExamQuestion
        fields = ('id', 'question', 'question_id', 'order')
        read_only_fields = ('id',)


class ExamScheduleSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ExamSchedule
        fields = ('id', 'exam', 'start_date', 'end_date', 'is_published', 
                  'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ExamSerializer(serializers.ModelSerializer):
    """Serializer for Exam model"""
    exam_questions = ExamQuestionSerializer(many=True, required=False, read_only=True)
    question_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    schedule = ExamScheduleSerializer(read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Exam
        fields = ('id', 'title', 'description', 'duration_minutes', 'passing_score',
                  'total_points', 'is_active', 'allow_retake', 'show_results_immediately',
                  'randomize_questions', 'randomize_options', 'created_by', 'created_by_name',
                  'exam_questions', 'question_ids', 'schedule', 'created_at', 'updated_at')
        read_only_fields = ('id', 'total_points', 'created_at', 'updated_at', 'created_by')
    
    def create(self, validated_data):
        question_ids = validated_data.pop('question_ids', [])
        exam = Exam.objects.create(**validated_data)
        
        # Add questions to exam
        for index, question_id in enumerate(question_ids):
            ExamQuestion.objects.create(
                exam=exam,
                question_id=question_id,
                order=index
            )
        
        exam.calculate_total_points()
        return exam
    
    def update(self, instance, validated_data):
        question_ids = validated_data.pop('question_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if question_ids is not None:
            # Remove existing questions
            instance.exam_questions.all().delete()
            # Add new questions
            for index, question_id in enumerate(question_ids):
                ExamQuestion.objects.create(
                    exam=instance,
                    question_id=question_id,
                    order=index
                )
            instance.calculate_total_points()
        
        return instance


class ExamListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for exam lists"""
    question_count = serializers.IntegerField(source='exam_questions.count', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    has_schedule = serializers.BooleanField(source='schedule', read_only=True)
    
    # New Fields
    student_status = serializers.SerializerMethodField()
    availability_window = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = ('id', 'title', 'duration_minutes', 'passing_score', 'total_points',
                  'is_active', 'question_count', 'created_by', 'created_by_name', 'has_schedule',
                  'created_at', 'student_status', 'availability_window')

    def get_student_status(self, obj):
        user = self.context.get('request').user
        if not user or not user.is_authenticated or not hasattr(user, 'exam_sessions'):
            return 'not_started'
            
        # Get latest session for this exam
        session = user.exam_sessions.filter(exam=obj).first()
        if not session:
            return 'not_started'
            
        # If pending and time up, mark as submitted essentially
        if session.status == 'in_progress' and session.check_time_limit():
            return 'time_up'
            
        return session.status

    def get_availability_window(self, obj):
        try:
            schedule = obj.schedule
        except Exception: # Catch ObjectDoesNotExist (implied via AttributeError or import)
            return {'is_open': obj.is_active, 'reason': 'Manual Trigger'}
            
        now = timezone.now()
        is_open = schedule.is_published and schedule.start_date <= now <= schedule.end_date
        
        return {
            'is_open': is_open,
            'start_date': schedule.start_date,
            'end_date': schedule.end_date,
            'is_published': schedule.is_published
        }

