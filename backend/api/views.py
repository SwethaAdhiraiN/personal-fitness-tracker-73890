from rest_framework.decorators import api_view
from rest_framework import generics, viewsets, status, permissions
from rest_framework.response import Response
from django.contrib.auth import login
from .models import WorkoutPlan, DailyWorkout, BodyComposition, ProgressTracking
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    WorkoutPlanSerializer, DailyWorkoutSerializer,
    BodyCompositionSerializer, ProgressTrackingSerializer
)
from django.contrib.auth import get_user_model
from rest_framework.views import APIView

User = get_user_model()

@api_view(['GET'])
def health(request):
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
class RegisterView(generics.CreateAPIView):
    """Registers a new user."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

# PUBLIC_INTERFACE
class LoginView(APIView):
    """Logs in a user and returns success if valid."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

# PUBLIC_INTERFACE
class CurrentUserView(APIView):
    """Get the current authenticated user's info."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# PUBLIC_INTERFACE
class WorkoutPlanViewSet(viewsets.ModelViewSet):
    """CRUD for Workout Plans (restricted to logged-in user)."""
    serializer_class = WorkoutPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkoutPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# PUBLIC_INTERFACE
class DailyWorkoutViewSet(viewsets.ModelViewSet):
    """CRUD for daily workouts. Must belong to a plan owned by user."""
    serializer_class = DailyWorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        plan_id = self.request.query_params.get('plan')
        qs = DailyWorkout.objects.filter(plan__user=self.request.user)
        if plan_id is not None:
            qs = qs.filter(plan__id=plan_id)
        return qs

    def perform_create(self, serializer):
        # User can only add to plans they own
        plan = serializer.validated_data['plan']
        if plan.user != self.request.user:
            raise permissions.PermissionDenied("Not your workout plan.")
        serializer.save()

# PUBLIC_INTERFACE
class BodyCompositionViewSet(viewsets.ModelViewSet):
    """CRUD for body composition. Restricted to the authenticated user."""
    serializer_class = BodyCompositionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BodyComposition.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# PUBLIC_INTERFACE
class ProgressTrackingViewSet(viewsets.ModelViewSet):
    """CRUD for tracking workout progress. Restricted to user."""
    serializer_class = ProgressTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProgressTracking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
