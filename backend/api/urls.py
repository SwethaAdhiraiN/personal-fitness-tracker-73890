from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health,
    RegisterView,
    LoginView,
    LogoutView,
    CurrentUserView,
    WorkoutPlanViewSet,
    DailyWorkoutViewSet,
    BodyCompositionViewSet,
    ProgressTrackingViewSet,
    WeeklyWorkoutPlanView,
    DailyWorkoutChecklistView,
    BodyFatEstimateView,
    ProgressAggregationView
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
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', CurrentUserView.as_view(), name='current-user'),

    path('my-weekly-workout/', WeeklyWorkoutPlanView.as_view(), name='my-weekly-workout'),
    path('daily-checklist/', DailyWorkoutChecklistView.as_view(), name='daily-workout-checklist'),
    path('estimate-body-fat/', BodyFatEstimateView.as_view(), name='estimate-body-fat'),
    path('progress-chart/', ProgressAggregationView.as_view(), name='progress-aggregation'),

    path('', include(router.urls)),
]
