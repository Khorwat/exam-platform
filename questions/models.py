from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class QuestionCategory(models.Model):
    """Category for organizing questions"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Question Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Question(models.Model):
    """Question model supporting multiple question types"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='medium')
    category = models.ForeignKey(QuestionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    points = models.PositiveIntegerField(default=1)
    explanation = models.TextField(blank=True, help_text="Explanation shown after exam")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_questions')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.question_text[:50]}... ({self.get_question_type_display()})"


class QuestionOption(models.Model):
    """Options for multiple choice and true/false questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['question', 'order']
    
    def __str__(self):
        return f"{self.question.question_text[:30]}... - {self.option_text[:30]}"

