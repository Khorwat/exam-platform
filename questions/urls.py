from django.urls import path
from .views import (
    QuestionCategoryListCreateView, QuestionCategoryDetailView,
    QuestionListCreateView, QuestionDetailView, bulk_delete_questions
)

urlpatterns = [
    path('categories/', QuestionCategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', QuestionCategoryDetailView.as_view(), name='category-detail'),
    path('', QuestionListCreateView.as_view(), name='question-list'),
    path('<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('bulk-delete/', bulk_delete_questions, name='question-bulk-delete'),
]

