from django.db import migrations


def create_periodic_task(apps, schema_editor):
    IntervalSchedule = apps.get_model("django_celery_beat", "IntervalSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=60,
        period="seconds",
    )
    PeriodicTask.objects.get_or_create(
        name="send-habit-reminders-every-minute",
        defaults={
            "interval": schedule,
            "task": "habits.tasks.send_reminders",
        },
    )


def delete_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name="send-habit-reminders-every-minute").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("habits", "0002_initial"),
        ("django_celery_beat", "0018_improve_crontab_helptext"),
    ]

    operations = [
        migrations.RunPython(create_periodic_task, delete_periodic_task),
    ]
