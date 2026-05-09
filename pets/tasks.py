from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import PetReport, Match
from .services import MatchingService
import logging

logger = logging.getLogger(__name__)


@shared_task
def sync_dog_breeds():
    """
    Tarea periódica para sincronizar razas desde THE DOG API.
    """
    from .services import DogAPIService
    
    try:
        breeds_data = DogAPIService.get_all_breeds(force_refresh=True)
        logger.info(f"Razas sincronizadas: {len(breeds_data)}")
        return f"Sincronizadas {len(breeds_data)} razas"
    except Exception as e:
        logger.error(f"Error sincronizando razas: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def find_matches_for_report(report_id):
    """
    Encuentra coincidencias para un reporte específico.
    """
    try:
        report = PetReport.objects.get(id=report_id)
        matches = MatchingService.find_matches(report, min_score=50)
        
        # Crear registros de Match
        for match_data in matches:
            if report.report_type == 'lost':
                Match.objects.get_or_create(
                    lost_report=report,
                    found_report=match_data['report'],
                    defaults={
                        'match_score': match_data['score'],
                        'match_reason': '\n'.join(match_data['reasons']),
                    }
                )
            else:
                Match.objects.get_or_create(
                    lost_report=match_data['report'],
                    found_report=report,
                    defaults={
                        'match_score': match_data['score'],
                        'match_reason': '\n'.join(match_data['reasons']),
                    }
                )
        
        logger.info(f"Se encontraron {len(matches)} coincidencias para reporte {report_id}")
        return f"Encontradas {len(matches)} coincidencias"
        
    except PetReport.DoesNotExist:
        logger.error(f"Reporte no encontrado: {report_id}")
        return "Reporte no encontrado"
    except Exception as e:
        logger.error(f"Error encontrando matches: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def send_match_notification(match_id):
    """
    Envía notificaciones sobre nuevas coincidencias.
    """
    try:
        match = Match.objects.get(id=match_id)
        
        # Notificar propietario de reporte perdido
        send_mail(
            subject=f"¡Posible coincidencia encontrada para {match.lost_report.pet_name}!",
            message=f"""
            Se encontró una posible coincidencia para tu reporte:
            
            Tu reporte: {match.lost_report.pet_name}
            Posible coincidencia: {match.found_report.pet_name}
            Puntuación de similitud: {match.match_score}%
            
            Razones:
            {match.match_reason}
            
            Accede a la plataforma para más detalles.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[match.lost_report.user.email]
        )
        
        # Notificar propietario de reporte encontrado
        send_mail(
            subject=f"Tu reporte de {match.found_report.pet_name} coincide con otro reporte",
            message=f"""
            Tu reporte de mascota encontrada coincide con:
            
            Tu reporte: {match.found_report.pet_name}
            Reporte perdido: {match.lost_report.pet_name}
            Puntuación de similitud: {match.match_score}%
            
            Razones:
            {match.match_reason}
            
            Accede a la plataforma para más detalles.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[match.found_report.user.email]
        )
        
        logger.info(f"Notificaciones enviadas para coincidencia {match_id}")
        return "Notificaciones enviadas"
        
    except Match.DoesNotExist:
        logger.error(f"Coincidencia no encontrada: {match_id}")
        return "Coincidencia no encontrada"
    except Exception as e:
        logger.error(f"Error enviando notificaciones: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def cleanup_archived_reports():
    """
    Tarea periódica para limpiar reportes archivados muy antiguos.
    """
    from datetime import timedelta
    from django.utils import timezone
    
    try:
        cutoff_date = timezone.now() - timedelta(days=180)
        old_reports = PetReport.objects.filter(
            status='archived',
            updated_at__lt=cutoff_date
        )
        count = old_reports.count()
        old_reports.delete()
        
        logger.info(f"Se eliminaron {count} reportes archivados antiguos")
        return f"Eliminados {count} reportes"
        
    except Exception as e:
        logger.error(f"Error limpiando reportes: {str(e)}")
        return f"Error: {str(e)}"
