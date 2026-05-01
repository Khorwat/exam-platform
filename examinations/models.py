from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from exams.models import Exam, ExamQuestion
from questions.models import Question, QuestionOption

User = get_user_model()


class ExamSession(models.Model):
    """Active exam session for a student"""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('time_up', 'Time Up'),
    ]
    
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sessions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    time_remaining_seconds = models.PositiveIntegerField(null=True, blank=True)
    grading_status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending Review'), ('graded', 'Reviewed')], 
        default='pending'
    )

    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['exam', 'student']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title} ({self.get_status_display()})"
    
    @property
    def is_active(self):
        """Check if session is currently active"""
        return self.status == 'in_progress'
    
    @property
    def time_elapsed_seconds(self):
        """Calculate time elapsed in seconds"""
        if self.submitted_at:
            return int((self.submitted_at - self.started_at).total_seconds())
        return int((timezone.now() - self.started_at).total_seconds())
    
    def check_time_limit(self):
        """Check if time limit has been exceeded"""
        if self.status != 'in_progress':
            return False
        
        elapsed = self.time_elapsed_seconds
        duration_seconds = self.exam.duration_minutes * 60
        
        if elapsed >= duration_seconds:
            self.status = 'time_up'
            self.submitted_at = timezone.now()
            self.save()
            return True
        return False
    
    def submit(self):
        """Mark exam as submitted"""
        if self.status == 'in_progress':
            self.status = 'submitted'
            self.submitted_at = timezone.now()
            self.save()


class ExamAnswer(models.Model):
    """Student's answer to a question in an exam"""
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(
        QuestionOption, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='exam_answers'
    )
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    answered_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['session', 'question']
        ordering = ['question__examquestion__order']
    
    def __str__(self):
        return f"{self.session.student.username} - {self.question.question_text[:30]}..."
    
    def calculate_score(self):
        """Calculate score for this answer"""
        if self.question.question_type == 'multiple_choice' or self.question.question_type == 'true_false':
            if self.selected_option and self.selected_option.is_correct:
                self.is_correct = True
                self.points_earned = self.question.points
            else:
                self.is_correct = False
                self.points_earned = 0
        self.save()


class ProctoringSnapshot(models.Model):
    """Webcam snapshot for proctoring"""
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='snapshots')
    image = models.ImageField(upload_to='proctoring/snapshots/%Y/%m/%d/')
    timestamp = models.DateTimeField(auto_now_add=True)
    trust_score = models.FloatField(default=1.0, help_text="AI calculated trust score (0.0-1.0)")
    issue_type = models.CharField(max_length=50, blank=True, null=True, help_text="Reason for low score")
    face_data = models.JSONField(null=True, blank=True, help_text="Face bounding box and landmarks")
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Snapshot for {self.session} at {self.timestamp}"
