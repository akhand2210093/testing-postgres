from rest_framework import serializers
from .models import User, Question, UserResponse, Answer, Leaderboard
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name','student_number', 'email']

    def validate_email(self, value):
        if not value.endswith('@akgec.ac.in'):
            raise serializers.ValidationError('Email must be in the domain @akgec.ac.in')
        return value


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'section', 'text', 'correct_answer']  # Only include the correct answer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'is_correct']

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = ['user', 'question', 'answer']

class LeaderboardSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Leaderboard
        fields = ['user', 'score']
