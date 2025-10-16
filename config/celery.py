# celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('hotel_yunuen')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Tareas programadas
app.conf.beat_schedule = {
    'update-room-availability-daily': {
        'task': 'bookings.tasks.update_all_room_availability',
        'schedule': crontab(hour=0, minute=0),  # Diario a medianoche
    },
    'check-expired-bookings': {
        'task': 'bookings.tasks.check_expired_bookings',
        'schedule': crontab(hour=1, minute=0),  # Diario a la 1 AM
    },
    'refresh-statistics-weekly': {
        'task': 'reviews.tasks.refresh_all_statistics',
        'schedule': crontab(day_of_week=1, hour=2, minute=0),  # Lunes 2 AM
    },
}