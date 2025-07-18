from rest_framework.decorators import api_view
from rest_framework import generics, viewsets, status, permissions
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .models import WorkoutPlan, DailyWorkout, BodyComposition, ProgressTracking
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    WorkoutPlanSerializer, DailyWorkoutSerializer,
    BodyCompositionSerializer, ProgressTrackingSerializer,
    BodyFatEstimateSerializer,
    DailyWorkoutChecklistSerializer
)
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

User = get_user_model()

@api_view(['GET'])
def health(request):
    """Returns health status of the API."""
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
class RegisterView(generics.CreateAPIView):
    """Registers a new user."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

# PUBLIC_INTERFACE
class LoginView(APIView):
    """Logs in a user and returns user data if valid."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

# PUBLIC_INTERFACE
class LogoutView(APIView):
    """Logs out the current authenticated user."""
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)

# PUBLIC_INTERFACE
class CurrentUserView(APIView):
    """Get the current authenticated user's info."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# PUBLIC_INTERFACE
class WeeklyWorkoutPlanView(APIView):
    """Get personalized weekly workout plans for the authenticated user."""
    permission_classes = [IsAuthenticated]
    def get(self, request):
        now = timezone.now().date()
        plans = WorkoutPlan.objects.filter(user=request.user, start_date__lte=now, end_date__gte=now, is_active=True)
        return Response(WorkoutPlanSerializer(plans, many=True).data)

# PUBLIC_INTERFACE
class DailyWorkoutChecklistView(APIView):
    """
    GET: Get daily workout schedule/checklist for a date (today by default).
    POST: Mark daily workout(s) completed/uncompleted [{id, completed}]
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Accept date param? Default: today
        date_str = request.query_params.get("date")
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            target_date = timezone.now().date()
        workouts = DailyWorkout.objects.filter(plan__user=request.user, date=target_date)
        return Response(DailyWorkoutSerializer(workouts, many=True).data)

    def post(self, request):
        if isinstance(request.data, dict):
            entries = [request.data]
        else:
            entries = request.data
        results = []
        for entry in entries:
            serializer = DailyWorkoutChecklistSerializer(data=entry)
            serializer.is_valid(raise_exception=True)
            try:
                obj = DailyWorkout.objects.get(id=serializer.validated_data['id'], plan__user=request.user)
            except DailyWorkout.DoesNotExist:
                continue
            obj.completed = serializer.validated_data['completed']
            obj.save()
            results.append(DailyWorkoutSerializer(obj).data)
        return Response(results)

# PUBLIC_INTERFACE
class BodyFatEstimateView(APIView):
    """
    POST user input (US Navy method): Returns estimated body fat percentage.
    Fields: sex ("male"/"female"), height_cm, neck_cm, waist_cm, (hips_cm - required for females)
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = BodyFatEstimateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        sex = data['sex']
        height = data['height_cm']
        neck = data['neck_cm']
        waist = data['waist_cm']
        hips = data.get('hips_cm', 0)
        import math
        if sex == "male":
            # US Navy Method (males)
            body_fat = 495 / (
                1.0324
                - 0.19077 * math.log10(waist - neck)
                + 0.15456 * math.log10(height)
            ) - 450
        else:
            # US Navy Method (females)
            if hips == 0:
                return Response({"error": "hips_cm required for female"}, status=status.HTTP_400_BAD_REQUEST)
            body_fat = 495 / (
                1.29579
                - 0.35004 * math.log10(waist + hips - neck)
                + 0.22100 * math.log10(height)
            ) - 450
        result = dict(data)
        result["body_fat"] = round(body_fat, 2)
        return Response(result)

# PUBLIC_INTERFACE
class ProgressAggregationView(APIView):
    """
    Get progress/chart endpoint.
    Aggregates progress for the current user, grouped by exercise name.
    ?exercise: filter by exercise_name (optional)
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Can filter by exercise_name
        exercise = request.query_params.get("exercise")
        qs = ProgressTracking.objects.filter(user=request.user)
        if exercise:
            qs = qs.filter(exercise_name=exercise)
        # For line chart: return [{label: date, value: total_volume}]
        results = [
            {"label": str(p.date), "value": float(p.total_volume)}
            for p in qs.order_by("date")
        ]
        return Response(results)

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
