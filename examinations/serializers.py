from rest_framework import serializers
from .models import ExamSession, ExamAnswer, ProctoringSnapshot
from exams.serializers import ExamSerializer
from questions.serializers import QuestionSerializer, QuestionOptionSerializer


class ExamAnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    selected_option = QuestionOptionSerializer(read_only=True)
    selected_option_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = ExamAnswer
        fields = ('id', 'session', 'question', 'selected_option', 'selected_option_id',
                  'is_correct', 'points_earned', 'answered_at')
        read_only_fields = ('id', 'is_correct', 'points_earned', 'answered_at')
    
    def create(self, validated_data):
        selected_option_id = validated_data.pop('selected_option_id', None)
        if selected_option_id:
            validated_data['selected_option_id'] = selected_option_id
        answer = ExamAnswer.objects.create(**validated_data)
        answer.calculate_score()
        return answer
    
    def update(self, instance, validated_data):
        selected_option_id = validated_data.pop('selected_option_id', None)
        if selected_option_id is not None:
            from questions.models import QuestionOption
            try:
                instance.selected_option = QuestionOption.objects.get(id=selected_option_id)
            except QuestionOption.DoesNotExist:
                pass
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.calculate_score()
        return instance


class ExamSessionSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)
    answers = ExamAnswerSerializer(many=True, read_only=True)
    time_elapsed_seconds = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ExamSession
        fields = ('id', 'exam', 'student', 'started_at', 'submitted_at', 'status',
                  'ip_address', 'time_remaining_seconds', 'time_elapsed_seconds',
                  'is_active', 'grading_status', 'answers')
        read_only_fields = ('id', 'started_at', 'submitted_at', 'status', 'student', 'grading_status')


class StartExamSessionSerializer(serializers.Serializer):
    """Serializer for starting an exam session"""
    exam_id = serializers.IntegerField()


class SubmitAnswerSerializer(serializers.Serializer):
    """Serializer for submitting an answer"""
    question_id = serializers.IntegerField()
    selected_option_id = serializers.IntegerField(required=False, allow_null=True)


class ProctoringSnapshotSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='session.student.username', read_only=True)
    exam_title = serializers.CharField(source='session.exam.title', read_only=True)

    class Meta:
        model = ProctoringSnapshot
        fields = ('id', 'session', 'student_name', 'exam_title', 'image', 'timestamp', 'trust_score', 'issue_type', 'face_data')
        read_only_fields = ('id', 'timestamp', 'trust_score', 'issue_type', 'face_data')
