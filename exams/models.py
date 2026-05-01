from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from questions.models import Question

User = get_user_model()


class Exam(models.Model):
    """Exam model for creating and managing exams"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(480)],
        help_text="Exam duration in minutes"
    )
    passing_score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=60,
        help_text="Minimum percentage required to pass"
    )
    total_points = models.PositiveIntegerField(default=0, editable=False)
    is_active = models.BooleanField(default=True)
    allow_retake = models.BooleanField(default=False)
    show_results_immediately = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=True)
    randomize_options = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def calculate_total_points(self):
        """Calculate total points from all questions"""
        total = self.exam_questions.aggregate(
            total=models.Sum('question__points')
        )['total'] or 0
        self.total_points = total
        self.save(update_fields=['total_points'])
        return total


class ExamQuestion(models.Model):
    """Many-to-many relationship between Exam and Question"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['exam', 'question']
    
    def __str__(self):
        return f"{self.exam.title} - {self.question.question_text[:30]}..."


class ExamSchedule(models.Model):
    """Schedule for when exams are available"""
    exam = models.OneToOneField(Exam, on_delete=models.CASCADE, related_name='schedule')
    start_date = models.DateTimeField(help_text="When the exam becomes available")
    end_date = models.DateTimeField(help_text="When the exam becomes unavailable")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.exam.title} - {self.start_date} to {self.end_date}"
    
    @property
    def is_active(self):
        """Check if exam is currently active based on schedule"""
        from django.utils import timezone
        now = timezone.now()
        return self.is_published and self.start_date <= now <= self.end_date

