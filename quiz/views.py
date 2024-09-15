from django.shortcuts import render

# Create your views here.
import requests
from django.conf import settings
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import User, Question, Answer, UserResponse, Leaderboard
from .serializers import (
    UserSerializer, QuestionSerializer, AnswerSerializer, UserResponseSerializer, LeaderboardSerializer
)




# Login API (or Create User)
class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name')
        student_number = data.get('student_number')
        email = data.get('email')
        # password = data.get('password')  # Get password from request data
        # recaptcha_response = data.get('g-recaptcha-response')

        # # Validate reCAPTCHA
        # recaptcha_verification_url = 'https://www.google.com/recaptcha/api/siteverify'
        # recaptcha_data = {
        #     'secret': settings.RECAPTCHA_SECRET_KEY,
        #     'response': recaptcha_response
        # }
        # recaptcha_verification = requests.post(recaptcha_verification_url, data=recaptcha_data)
        # recaptcha_result = recaptcha_verification.json()

        # if not recaptcha_result.get('success'):
        #     return Response({'detail': 'Invalid reCAPTCHA. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email domain
        if not email.endswith('@akgec.ac.in'):
            return Response({'detail': 'Email must be in the domain @akgec.ac.in'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for unique student number and email
        if User.objects.filter(student_number=student_number).exists():
            return Response({'detail': 'Student number already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Password validation
        # expected_password = f'{student_number}@AKGEC'
        # if password != expected_password:
        #     return Response({'detail': 'Invalid password. The password should be in the format {student_number}@AKGEC.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create or retrieve user
        user, created = User.objects.get_or_create(
            student_number=student_number,
            defaults={'email': email, 'name': name}
        )

        if not created and user.email != email:
            return Response({'detail': 'Email does not match existing record.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'user': UserSerializer(user).data,
            'access_token': access_token,
            'refresh_token': str(refresh)
        }, status=status.HTTP_200_OK)


# View to add questions and answers
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def create(self, request, *args, **kwargs):
        questions_data = request.data.get('questions', [])
        created_questions = []

        for question_data in questions_data:
            question_info = question_data.get('question')
            
            question = Question.objects.create(**question_info)
            created_questions.append(question)

        serializer = self.get_serializer(created_questions, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# View all questions
class QuestionListView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

# Submit all responses at once
from rest_framework.exceptions import NotFound

class SubmitResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            responses = request.data.get('responses', [])
            user = request.user
            score_increment = 0  # This will store the score for this particular submission

            for response in responses:
                question = get_object_or_404(Question, id=response['question_id'])
                submitted_answer = response['answer_text'].strip().lower()

                # Check if the submitted answer matches the correct answer
                if submitted_answer == question.correct_answer.strip().lower():
                    score_increment += 4
                else:
                    score_increment -= 1

                # Store the user's response (whether correct or not)
                UserResponse.objects.create(user=user, question=question, answer_text=submitted_answer)

            # Update or create the leaderboard entry for the user
            leaderboard, created = Leaderboard.objects.get_or_create(user=user)
            leaderboard.score += score_increment  # Add the current submission's score to the existing score
            leaderboard.save()

            return Response({'score': leaderboard.score}, status=status.HTTP_200_OK)
        
        except NotFound:
            return Response({'detail': 'User or Question not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# View user score
class UserScoreView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaderboardSerializer

    def get_object(self):
        return get_object_or_404(Leaderboard, user=self.request.user)

# View leaderboard
class LeaderboardView(generics.ListAPIView):
    queryset = Leaderboard.objects.all().order_by('-score')
    serializer_class = LeaderboardSerializer

