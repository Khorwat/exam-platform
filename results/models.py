from django.db import models
from django.contrib.auth import get_user_model
from examinations.models import ExamSession

User = get_user_model()


class ExamResult(models.Model):
    """Final result for a completed exam session"""
    session = models.OneToOneField(ExamSession, on_delete=models.CASCADE, related_name='result')
    total_points_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_points_possible = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    percentage_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    passed = models.BooleanField(default=False)
    graded_at = models.DateTimeField(auto_now_add=True)
    graded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='graded_results'
    )
    
    class Meta:
        ordering = ['-graded_at']
    
    def __str__(self):
        return f"{self.session.student.username} - {self.session.exam.title} ({self.percentage_score}%)"
    
    def calculate_score(self):
        """Calculate total score from all answers"""
        total_earned = sum(answer.points_earned for answer in self.session.answers.all())
        total_possible = self.session.exam.total_points
        
        self.total_points_earned = total_earned
        self.total_points_possible = total_possible
        self.percentage_score = (total_earned / total_possible * 100) if total_possible > 0 else 0
        self.passed = self.percentage_score >= self.session.exam.passing_score
        self.save()


class PerformanceAnalytics(models.Model):
    """Analytics data for performance tracking"""
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='analytics')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_analytics')
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_exams_taken = models.PositiveIntegerField(default=0)
    total_passed = models.PositiveIntegerField(default=0)
    total_failed = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['exam', 'student']
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title} Analytics"
    
    def update_analytics(self):
        """Update analytics based on all results for this student and exam"""
        results = ExamResult.objects.filter(
            session__exam=self.exam,
            session__student=self.student
        )
        
        self.total_exams_taken = results.count()
        self.total_passed = results.filter(passed=True).count()
        self.total_failed = results.filter(passed=False).count()
        
        if self.total_exams_taken > 0:
            avg = results.aggregate(avg=models.Avg('percentage_score'))['avg'] or 0
            self.average_score = avg
        
        self.save()

