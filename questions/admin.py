from django.contrib import admin
from .models import QuestionCategory, Question, QuestionOption


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 2


@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_type', 'difficulty', 'category', 'points', 'is_active', 'created_at')
    list_filter = ('question_type', 'difficulty', 'category', 'is_active', 'created_at')
    search_fields = ('question_text', 'explanation')
    inlines = [QuestionOptionInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'option_text', 'is_correct', 'order')
    list_filter = ('is_correct',)
    search_fields = ('option_text', 'question__question_text')

