from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 
                  'student_id', 'phone_number', 'date_of_birth', 'profile_picture', 
                  'is_active', 'password', 'created_at')
        read_only_fields = ('id', 'created_at')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
    
    def validate_password(self, value):
        if value:
            validate_password(value)
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 
                  'last_name', 'role', 'student_id', 'phone_number', 'date_of_birth')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        # Handle optional student_id
        if 'student_id' in validated_data and not validated_data['student_id']:
            validated_data['student_id'] = None
            
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (read-only for students)"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 
                  'student_id', 'phone_number', 'date_of_birth', 'profile_picture', 
                  'created_at')
        read_only_fields = ('id', 'username', 'role', 'created_at')

