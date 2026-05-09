# Configuración de Celery Beat
# Agregar esto a settings.py si es necesario

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Sincronizar razas cada 7 días
    'sync-dog-breeds': {
        'task': 'pets.tasks.sync_dog_breeds',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Domingos a las 2 AM
    },
    # Limpiar reportes archivados cada 30 días
    'cleanup-archived-reports': {
        'task': 'pets.tasks.cleanup_archived_reports',
        'schedule': crontab(hour=3, minute=0, day_of_month=1),  # Primer día del mes a las 3 AM
    },
}
