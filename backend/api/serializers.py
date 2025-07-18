from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import WorkoutPlan, DailyWorkout, BodyComposition, ProgressTracking

User = get_user_model()

# PUBLIC_INTERFACE
class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'date_of_birth',
            'gender'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            date_of_birth=validated_data.get('date_of_birth', None),
            gender=validated_data.get('gender', None)
        )
        return user

# PUBLIC_INTERFACE
class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login authentication."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            data['user'] = user
            return data
        raise serializers.ValidationError("Invalid credentials.")

# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """Serializer for displaying user details."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_of_birth', 'gender']

# PUBLIC_INTERFACE
class WorkoutPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutPlan
        fields = '__all__'
        read_only_fields = ['user']

# PUBLIC_INTERFACE
class DailyWorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyWorkout
        fields = '__all__'
        read_only_fields = ['plan']

# PUBLIC_INTERFACE
class BodyCompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyComposition
        fields = '__all__'
        read_only_fields = ['user']

# PUBLIC_INTERFACE
class ProgressTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressTracking
        fields = '__all__'
        read_only_fields = ['user']
