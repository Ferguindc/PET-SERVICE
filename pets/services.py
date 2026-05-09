import requests
import logging
from django.conf import settings
from django.core.cache import cache
from .models import Breed
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class DogAPIService:
    """
    Servicio para integración con THE DOG API.
    Documentación: https://www.thedogapi.com/
    """
    
    BASE_URL = settings.DOG_API_BASE_URL
    API_KEY = settings.DOG_API_KEY
    CACHE_TIMEOUT = 60 * 60 * 24  # 24 horas
    
    @classmethod
    def get_all_breeds(cls, force_refresh=False):
        """
        Obtiene todas las razas de THE DOG API y las almacena en caché local.
        """
        cache_key = 'dog_api_breeds'
        
        if not force_refresh:
            cached_breeds = cache.get(cache_key)
            if cached_breeds:
                return cached_breeds
        
        try:
            headers = {}
            if cls.API_KEY:
                headers['x-api-key'] = cls.API_KEY
            
            response = requests.get(
                f"{cls.BASE_URL}/breeds",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            breeds_data = response.json()
            
            # Sincronizar con base de datos local
            cls._sync_breeds_to_db(breeds_data)
            
            # Cachear resultado
            cache.set(cache_key, breeds_data, cls.CACHE_TIMEOUT)
            
            logger.info(f"Se obtuvieron {len(breeds_data)} razas de THE DOG API")
            return breeds_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener razas de THE DOG API: {str(e)}")
            
            # Retornar razas del caché local
            local_breeds = Breed.objects.all().values(
                'id', 'api_id', 'name', 'image_url',
                'height_min', 'height_max', 'weight_min', 'weight_max'
            )
            return list(local_breeds)
    
    @classmethod
    def _sync_breeds_to_db(cls, breeds_data):
        """
        Sincroniza las razas obtenidas de THE DOG API con la base de datos local.
        """
        for breed_data in breeds_data:
            try:
                breed_dict = {
                    'api_id': str(breed_data.get('id', '')),
                    'name': breed_data.get('name', ''),
                    'image_url': breed_data.get('image', {}).get('url', '') if breed_data.get('image') else '',
                }
                
                # Extraer dimensiones
                if breed_data.get('height'):
                    height_parts = str(breed_data['height']).split('-')
                    if len(height_parts) == 2:
                        try:
                            breed_dict['height_min'] = float(height_parts[0].strip())
                            breed_dict['height_max'] = float(height_parts[1].strip().split()[0])
                        except ValueError:
                            pass
                
                if breed_data.get('weight'):
                    weight_parts = str(breed_data['weight']).split('-')
                    if len(weight_parts) == 2:
                        try:
                            breed_dict['weight_min'] = float(weight_parts[0].strip())
                            breed_dict['weight_max'] = float(weight_parts[1].strip().split()[0])
                        except ValueError:
                            pass
                
                Breed.objects.update_or_create(
                    api_id=breed_dict['api_id'],
                    defaults=breed_dict
                )
            except Exception as e:
                logger.warning(f"Error sincronizando raza: {str(e)}")
                continue
    
    @classmethod
    def get_breed_by_id(cls, breed_id):
        """
        Obtiene una raza específica por su ID de THE DOG API.
        """
        try:
            headers = {}
            if cls.API_KEY:
                headers['x-api-key'] = cls.API_KEY
            
            response = requests.get(
                f"{cls.BASE_URL}/breeds/{breed_id}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener raza {breed_id}: {str(e)}")
            return None
    
    @classmethod
    def search_breeds(cls, query):
        """
        Busca razas por nombre.
        """
        try:
            all_breeds = cls.get_all_breeds()
            query_lower = query.lower()
            
            results = [
                breed for breed in all_breeds
                if query_lower in breed.get('name', '').lower()
            ]
            
            return results
            
        except Exception as e:
            logger.error(f"Error buscando razas: {str(e)}")
            return []


class MatchingService:
    """
    Servicio para detectar coincidencias entre mascotas perdidas y encontradas.
    Utilizado por el Match Service.
    """
    
    # Pesos para el cálculo de similitud
    WEIGHTS = {
        'breed': 0.30,
        'color': 0.25,
        'size': 0.20,
        'location': 0.15,
        'date': 0.10,
    }
    
    @staticmethod
    def calculate_similarity_score(lost_report, found_report):
        """
        Calcula un puntaje de similitud entre dos reportes (0-100).
        """
        score = 0
        reasons = []
        
        # Similitud de raza
        if lost_report.breed_id and found_report.breed_id:
            if lost_report.breed_id == found_report.breed_id:
                score += 100 * MatchingService.WEIGHTS['breed']
                reasons.append("Raza coincide exactamente")
            else:
                score += 30 * MatchingService.WEIGHTS['breed']
                reasons.append("Razas diferentes pero similares")
        elif lost_report.breed_custom and found_report.breed_custom:
            if lost_report.breed_custom.lower() == found_report.breed_custom.lower():
                score += 100 * MatchingService.WEIGHTS['breed']
                reasons.append("Raza personalizada coincide")
        
        # Similitud de color
        color_similarity = MatchingService._calculate_text_similarity(
            lost_report.color, found_report.color
        )
        score += (color_similarity * 100) * MatchingService.WEIGHTS['color']
        if color_similarity > 0.7:
            reasons.append("Color muy similar")
        
        # Similitud de tamaño
        if lost_report.size == found_report.size:
            score += 100 * MatchingService.WEIGHTS['size']
            reasons.append("Tamaño coincide")
        else:
            size_similarity = MatchingService._calculate_size_similarity(
                lost_report.size, found_report.size
            )
            score += (size_similarity * 100) * MatchingService.WEIGHTS['size']
        
        # Proximidad geográfica
        distance_km = MatchingService._calculate_distance(
            lost_report.latitude, lost_report.longitude,
            found_report.latitude, found_report.longitude
        )
        
        if distance_km <= 5:  # Menos de 5 km
            location_score = max(0, 1 - (distance_km / 5))
            score += (location_score * 100) * MatchingService.WEIGHTS['location']
            reasons.append(f"Muy cerca geográficamente ({distance_km:.1f} km)")
        else:
            score += 0  # No es relevante si está muy lejos
        
        # Similitud temporal
        time_diff_days = abs(
            (lost_report.date_incident - found_report.date_incident).days
        )
        
        if time_diff_days <= 7:  # Dentro de 7 días
            date_score = max(0, 1 - (time_diff_days / 7))
            score += (date_score * 100) * MatchingService.WEIGHTS['date']
            reasons.append(f"Reportes cercanos en tiempo ({time_diff_days} días)")
        
        return {
            'score': round(score, 2),
            'reasons': reasons
        }
    
    @staticmethod
    def _calculate_text_similarity(text1, text2):
        """
        Calcula similitud entre dos textos (0-1) usando secuencia similar.
        """
        from difflib import SequenceMatcher
        if not text1 or not text2:
            return 0
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    @staticmethod
    def _calculate_size_similarity(size1, size2):
        """
        Calcula similitud entre dos tamaños.
        """
        size_order = ['small', 'medium', 'large', 'giant']
        try:
            idx1 = size_order.index(size1)
            idx2 = size_order.index(size2)
            diff = abs(idx1 - idx2)
            return max(0, 1 - (diff * 0.3))
        except ValueError:
            return 0
    
    @staticmethod
    def _calculate_distance(lat1, lon1, lat2, lon2):
        """
        Calcula la distancia en kilómetros entre dos coordenadas
        usando la fórmula de Haversine.
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Radio de la Tierra en km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def find_matches(report, min_score=50):
        """
        Encuentra posibles coincidencias para un reporte dado.
        """
        from .models import PetReport, Match
        
        # Determinar el tipo opuesto
        opposite_type = 'found' if report.report_type == 'lost' else 'lost'
        
        # Buscar reportes del tipo opuesto dentro de un radio
        candidates = PetReport.objects.filter(
            report_type=opposite_type,
            status='active'
        ).exclude(id=report.id)
        
        matches_found = []
        
        for candidate in candidates:
            similarity = MatchingService.calculate_similarity_score(
                report, candidate
            )
            
            if similarity['score'] >= min_score:
                matches_found.append({
                    'report': candidate,
                    'score': similarity['score'],
                    'reasons': similarity['reasons']
                })
        
        # Ordenar por puntuación descendente
        matches_found.sort(key=lambda x: x['score'], reverse=True)
        
        return matches_found
