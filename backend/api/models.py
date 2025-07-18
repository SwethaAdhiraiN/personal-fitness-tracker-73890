from django.db import models
from django.contrib.auth.models import AbstractUser

# PUBLIC_INTERFACE
class User(AbstractUser):
    """
    Custom User model.
    Inherits Django's AbstractUser, includes username, email, password, etc. Add fitness-related fields as needed.
    """
    # Optionally, add additional fields like date_of_birth, etc.
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=16, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], null=True, blank=True)
    # Add further customization if required (e.g. premium status, avatar, etc.)
    def __str__(self):
        return self.username

# PUBLIC_INTERFACE
class WorkoutPlan(models.Model):
    """
    A user's personalized weekly workout plan.
    Each plan belongs to a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_plans')
    start_date = models.DateField()
    end_date = models.DateField()
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} | {self.user.username} | {self.start_date:%b %d %Y}"

# PUBLIC_INTERFACE
class DailyWorkout(models.Model):
    """
    A workout scheduled for a specific day within a user's workout plan.
    Adds fields for actual sets/reps and notes for granular checklist/progress tracking.
    """
    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='daily_workouts')
    date = models.DateField()
    # The kind of exercise (could be functionally split further by type)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    sets = models.PositiveIntegerField(default=0)
    reps = models.PositiveIntegerField(default=0)
    weight = models.FloatField(default=0.0, help_text='Weight in kilograms (if strength exercise)')
    duration_minutes = models.PositiveIntegerField(default=0, help_text='Duration in minutes (if cardio)')
    rest_seconds = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    # NEW: actual values completed, optional
    actual_sets = models.PositiveIntegerField(null=True, blank=True, help_text='Actual number of sets performed')
    actual_reps = models.PositiveIntegerField(null=True, blank=True, help_text='Actual number of reps performed per set')
    notes = models.TextField(blank=True, help_text='Notes or comments on this workout/completion')

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.name} on {self.date} | Plan: {self.plan}"

# PUBLIC_INTERFACE
class BodyComposition(models.Model):
    """
    Stores user's body composition metrics/bio-markers for tracking progress (such as weight, body fat, etc).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='body_compositions')
    date = models.DateField()
    weight_kg = models.FloatField()
    height_cm = models.FloatField()
    body_fat_percentage = models.FloatField(null=True, blank=True)
    waist_cm = models.FloatField(null=True, blank=True)
    hips_cm = models.FloatField(null=True, blank=True)
    chest_cm = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'date')

    def __str__(self):
        return f"BodyComp {self.user.username} - {self.date}"

# PUBLIC_INTERFACE
class ProgressTracking(models.Model):
    """
    Tracks workout progress for progressive overload, e.g. bests/lifts over time per exercise.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    exercise_name = models.CharField(max_length=128)
    date = models.DateField()
    best_set_weight = models.FloatField(default=0.0)
    best_set_reps = models.PositiveIntegerField(default=0)
    total_volume = models.FloatField(default=0.0, help_text='Sum of (weight * reps * sets) per session')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'exercise_name', 'date')

    def __str__(self):
        return f"{self.user.username} {self.exercise_name} {self.date:%Y-%m-%d}"

