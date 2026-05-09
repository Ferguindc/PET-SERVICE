from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PetReport, UserProfile, Match
from .tasks import find_matches_for_report, send_match_notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea un perfil de usuario automáticamente cuando se crea un usuario.
    """
    if created:
        UserProfile.objects.create(user=instance)
        logger.info(f"Perfil creado para usuario: {instance.username}")


@receiver(post_save, sender=PetReport)
def on_report_created(sender, instance, created, **kwargs):
    """
    Cuando se crea un nuevo reporte:
    1. Encontrar coincidencias automáticamente
    2. Enviar notificaciones
    """
    if created:
        logger.info(f"Nuevo reporte creado: {instance.report_id}")
        
        # Ejecutar búsqueda de coincidencias de forma asincrónica
        try:
            find_matches_for_report.delay(instance.id)
        except Exception as e:
            logger.error(f"Error al buscar coincidencias: {str(e)}")
            # Ejecutar sincronamente si Celery no está disponible
            from .services import MatchingService
            matches = MatchingService.find_matches(instance, min_score=50)
            for match_data in matches:
                if instance.report_type == 'lost':
                    match_obj, _ = Match.objects.get_or_create(
                        lost_report=instance,
                        found_report=match_data['report'],
                        defaults={
                            'match_score': match_data['score'],
                            'match_reason': '\n'.join(match_data['reasons']),
                        }
                    )
                else:
                    match_obj, _ = Match.objects.get_or_create(
                        lost_report=match_data['report'],
                        found_report=instance,
                        defaults={
                            'match_score': match_data['score'],
                            'match_reason': '\n'.join(match_data['reasons']),
                        }
                    )


@receiver(post_save, sender=Match)
def on_match_created(sender, instance, created, **kwargs):
    """
    Cuando se crea una nueva coincidencia, enviar notificaciones.
    """
    if created:
        logger.info(f"Nueva coincidencia creada: {instance.id}")
        
        try:
            send_match_notification.delay(instance.id)
        except Exception as e:
            logger.error(f"Error enviando notificación: {str(e)}")
