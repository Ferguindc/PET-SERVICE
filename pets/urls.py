from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetReportViewSet, BreedViewSet, MatchViewSet

router = DefaultRouter()
router.register(r'breeds', BreedViewSet, basename='breed')
router.register(r'reports', PetReportViewSet, basename='pet-report')
router.register(r'matches', MatchViewSet, basename='match')

urlpatterns = [
    path('', include(router.urls)),
]
