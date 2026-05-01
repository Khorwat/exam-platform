"""
Tests for questions app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Question, QuestionCategory, QuestionOption

User = get_user_model()


class QuestionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )
        self.category = QuestionCategory.objects.create(name='Math')
        self.question = Question.objects.create(
            question_text='What is 2+2?',
            question_type='multiple_choice',
            difficulty='easy',
            category=self.category,
            points=5,
            created_by=self.user
        )
        self.option1 = QuestionOption.objects.create(
            question=self.question,
            option_text='4',
            is_correct=True,
            order=1
        )
        self.option2 = QuestionOption.objects.create(
            question=self.question,
            option_text='5',
            is_correct=False,
            order=2
        )
    
    def test_question_creation(self):
        self.assertEqual(self.question.question_text, 'What is 2+2?')
        self.assertEqual(self.question.question_type, 'multiple_choice')
        self.assertEqual(self.question.options.count(), 2)
    
    def test_correct_option(self):
        correct_option = self.question.options.filter(is_correct=True).first()
        self.assertEqual(correct_option.option_text, '4')


class QuestionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )
        self.client.force_authenticate(user=self.user)
        self.category = QuestionCategory.objects.create(name='Math')
    
    def test_create_question(self):
        response = self.client.post('/api/questions/', {
            'question_text': 'What is 3+3?',
            'question_type': 'multiple_choice',
            'difficulty': 'easy',
            'category': self.category.id,
            'points': 5,
            'options': [
                {'option_text': '6', 'is_correct': True, 'order': 1},
                {'option_text': '7', 'is_correct': False, 'order': 2}
            ]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Question.objects.filter(question_text='What is 3+3?').exists())
    
    def test_list_questions(self):
        Question.objects.create(
            question_text='Test question',
            question_type='multiple_choice',
            created_by=self.user
        )
        response = self.client.get('/api/questions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

