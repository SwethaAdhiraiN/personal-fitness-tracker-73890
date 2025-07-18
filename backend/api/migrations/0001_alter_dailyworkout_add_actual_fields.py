from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '__init__'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyworkout',
            name='actual_sets',
            field=models.PositiveIntegerField(null=True, blank=True, help_text='Actual number of sets performed'),
        ),
        migrations.AddField(
            model_name='dailyworkout',
            name='actual_reps',
            field=models.PositiveIntegerField(null=True, blank=True, help_text='Actual number of reps performed per set'),
        ),
        migrations.AddField(
            model_name='dailyworkout',
            name='notes',
            field=models.TextField(blank=True, help_text='Notes or comments on this workout/completion'),
        ),
    ]
