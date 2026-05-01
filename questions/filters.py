import django_filters
from .models import Question


class QuestionFilter(django_filters.FilterSet):
    question_type = django_filters.ChoiceFilter(choices=Question.QUESTION_TYPES)
    difficulty = django_filters.ChoiceFilter(choices=Question.DIFFICULTY_LEVELS)
    category = django_filters.NumberFilter(field_name='category__id')
    
    class Meta:
        model = Question
        fields = ['question_type', 'difficulty', 'category', 'is_active']

