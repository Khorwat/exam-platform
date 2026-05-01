from rest_framework import serializers
from .models import QuestionCategory, Question, QuestionOption


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ('id', 'option_text', 'is_correct', 'order')
        read_only_fields = ('id',)


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model"""
    options = QuestionOptionSerializer(many=True, required=False)
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'difficulty', 'category', 
                  'category_name', 'points', 'explanation', 'created_by', 'created_by_name',
                  'is_active', 'options', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        question = Question.objects.create(**validated_data)
        for option_data in options_data:
            QuestionOption.objects.create(question=question, **option_data)
        return question
    
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if options_data is not None:
            # Delete existing options
            instance.options.all().delete()
            # Create new options
            for option_data in options_data:
                QuestionOption.objects.create(question=instance, **option_data)
        
        return instance


class QuestionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for question lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    option_count = serializers.IntegerField(source='options.count', read_only=True)
    
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'difficulty', 'category', 
                  'category_name', 'points', 'is_active', 'option_count', 'created_at')


class QuestionCategorySerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(source='question_set.count', read_only=True)
    
    class Meta:
        model = QuestionCategory
        fields = ('id', 'name', 'description', 'question_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

