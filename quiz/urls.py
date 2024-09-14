from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserLoginView, QuestionViewSet, QuestionListView,
    SubmitResponseView, UserScoreView, LeaderboardView
)

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='questions')

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('questionlist/', QuestionListView.as_view(), name='question-list'),
    path('submit-responses/', SubmitResponseView.as_view(), name='submit-responses'),
    path('score/', UserScoreView.as_view(), name='user-score'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('', include(router.urls)),
]

