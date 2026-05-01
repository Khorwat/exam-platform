from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ExamQuestion

@receiver(post_save, sender=ExamQuestion)
@receiver(post_delete, sender=ExamQuestion)
def update_exam_total_points(sender, instance, **kwargs):
    """Update exam total points when questions are added or removed"""
    instance.exam.calculate_total_points()
