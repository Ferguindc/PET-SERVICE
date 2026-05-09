from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
import logging
from django.utils import timezone
from django.db.models import Q

from .models import PetReport, Breed, Match, UserProfile
from .serializers import (
    PetReportSerializer, PetReportCreateUpdateSerializer,
    PetReportListSerializer, BreedSerializer, MatchSerializer
)
from .services import DogAPIService, MatchingService
from .permissions import IsOwnerOrReadOnly, IsAuthenticatedForCreate

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BreedFilter(FilterSet):
    class Meta:
        model = Breed
        fields = ['name']


class BreedViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para razas de perros.
    
    Proporciona endpoints para:
    - Listar todas las razas
    - Obtener detalles de una raza
    - Sincronizar razas con THE DOG API
    """
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BreedFilter
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    pagination_class = StandardResultsSetPagination
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def sync_from_api(self, request):
        """
        Sincroniza las razas desde THE DOG API.
        Solo para administradores.
        """
        if not request.user.is_staff:
            return Response(
                {'detail': 'No tienes permiso para sincronizar razas.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            breeds_data = DogAPIService.get_all_breeds(force_refresh=True)
            return Response({
                'message': f'Se sincronizaron {len(breeds_data)} razas correctamente.',
                'count': len(breeds_data)
            })
        except Exception as e:
            logger.error(f"Error sincronizando razas: {str(e)}")
            return Response(
                {'error': f'Error al sincronizar: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Busca razas por nombre.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Proporciona un parámetro "q" para buscar.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = DogAPIService.search_breeds(query)
        return Response({'results': results})


class PetReportFilter(FilterSet):
    class Meta:
        model = PetReport
        fields = {
            'report_type': ['exact'],
            'status': ['exact'],
            'size': ['exact'],
            'breed': ['exact'],
            'priority': ['gte', 'lte'],
            'date_incident': ['gte', 'lte'],
        }


class PetReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet para reportes de mascotas.
    
    Proporciona endpoints para:
    - Crear, listar, actualizar y eliminar reportes
    - Obtener coincidencias para un reporte
    - Filtrar y buscar reportes
    - Obtener reportes del usuario autenticado
    """
    queryset = PetReport.objects.select_related('user', 'breed').prefetch_related('images')
    serializer_class = PetReportSerializer
    permission_classes = [IsAuthenticatedForCreate, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PetReportFilter
    search_fields = ['pet_name', 'breed__name', 'location_description', 'color']
    ordering_fields = ['created_at', 'date_incident', 'priority', 'status']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PetReportCreateUpdateSerializer
        elif self.action == 'list':
            return PetReportListSerializer
        return PetReportSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """
        Obtiene las coincidencias para un reporte específico.
        """
        try:
            report = self.get_object()
            matches = MatchingService.find_matches(report, min_score=50)
            
            response_data = {
                'report_id': report.report_id,
                'matches_found': len(matches),
                'matches': [
                    {
                        'report_id': m['report'].report_id,
                        'pet_name': m['report'].pet_name,
                        'score': m['score'],
                        'reasons': m['reasons'],
                        'url': f"/api/v1/pets/reports/{m['report'].id}/"
                    }
                    for m in matches
                ]
            }
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error calculando matches: {str(e)}")
            return Response(
                {'error': 'Error al calcular coincidencias.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def mark_resolved(self, request, pk=None):
        """
        Marca un reporte como resuelto.
        """
        report = self.get_object()
        
        if report.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'No tienes permiso para hacer esto.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        report.status = 'resolved'
        report.resolution_notes = request.data.get('resolution_notes', '')
        report.save()
        
        return Response({
            'message': 'Reporte marcado como resuelto.',
            'report': PetReportSerializer(report).data
        })
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Archiva un reporte.
        """
        report = self.get_object()
        
        if report.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'No tienes permiso para hacer esto.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        report.status = 'archived'
        report.save()
        
        return Response({'message': 'Reporte archivado.'})
    
    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """
        Obtiene todos los reportes del usuario autenticado.
        """
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Debes estar autenticado.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        reports = PetReport.objects.filter(user=request.user).select_related('breed').prefetch_related('images')
        
        # Aplicar filtros y búsqueda manualmente si es necesario
        page = self.paginate_queryset(reports)
        if page is not None:
            serializer = PetReportListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PetReportListSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Obtiene reportes filtrados por tipo (lost/found).
        """
        report_type = request.query_params.get('type')
        
        if report_type not in ['lost', 'found']:
            return Response(
                {'error': 'El parámetro "type" debe ser "lost" o "found".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reports = PetReport.objects.filter(
            report_type=report_type,
            status='active'
        ).select_related('breed').prefetch_related('images')
        
        page = self.paginate_queryset(reports)
        if page is not None:
            serializer = PetReportListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PetReportListSerializer(reports, many=True)
        return Response(serializer.data)


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para coincidencias entre reportes.
    
    Proporciona endpoints para:
    - Listar coincidencias
    - Obtener detalles de una coincidencia
    - Confirmar o rechazar coincidencias
    """
    queryset = Match.objects.select_related('lost_report', 'found_report').order_by('-match_score')
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'lost_report', 'found_report']
    ordering_fields = ['match_score', 'created_at']
    pagination_class = StandardResultsSetPagination
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirma una coincidencia.
        """
        match = self.get_object()
        
        # Verificar que el usuario es propietario de uno de los reportes
        if match.lost_report.user != request.user and match.found_report.user != request.user:
            return Response(
                {'detail': 'No tienes permiso para confirmar esta coincidencia.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        match.status = 'confirmed'
        match.save()
        
        return Response({
            'message': 'Coincidencia confirmada.',
            'match': MatchSerializer(match).data
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Rechaza una coincidencia.
        """
        match = self.get_object()
        
        if match.lost_report.user != request.user and match.found_report.user != request.user:
            return Response(
                {'detail': 'No tienes permiso para rechazar esta coincidencia.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        match.status = 'rejected'
        match.save()
        
        return Response({'message': 'Coincidencia rechazada.'})
    
    @action(detail=False, methods=['get'])
    def my_matches(self, request):
        """
        Obtiene coincidencias relacionadas con reportes del usuario.
        """
        matches = Match.objects.filter(
            Q(lost_report__user=request.user) | Q(found_report__user=request.user)
        ).select_related('lost_report', 'found_report').order_by('-match_score')
        
        page = self.paginate_queryset(matches)
        if page is not None:
            serializer = MatchSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)
