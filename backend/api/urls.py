from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health,
    RegisterView,
    LoginView,
    CurrentUserView,
    WorkoutPlanViewSet,
    DailyWorkoutViewSet,
    BodyCompositionViewSet,
    ProgressTrackingViewSet
)

router = DefaultRouter()
router.register(r'workout-plans', WorkoutPlanViewSet, basename='workoutplan')
router.register(r'daily-workouts', DailyWorkoutViewSet, basename='dailyworkout')
router.register(r'body-compositions', BodyCompositionViewSet, basename='bodycomposition')
router.register(r'progress', ProgressTrackingViewSet, basename='progresstracking')

urlpatterns = [
    path('health/', health, name='Health'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('', include(router.urls)),
]
