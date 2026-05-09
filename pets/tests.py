from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, timedelta
from .models import PetReport, Breed, Match, PetReportImage
from .services import MatchingService, DogAPIService


class BreedModelTests(TestCase):
    """Tests para el modelo Breed"""
    
    def setUp(self):
        self.breed = Breed.objects.create(
            api_id="1",
            name="Labrador Retriever",
            height_min=55.0,
            height_max=57.0,
            weight_min=25.0,
            weight_max=36.0
        )
    
    def test_breed_creation(self):
        self.assertEqual(self.breed.name, "Labrador Retriever")
        self.assertEqual(self.breed.api_id, "1")
    
    def test_breed_str(self):
        self.assertEqual(str(self.breed), "Labrador Retriever")


class PetReportModelTests(TestCase):
    """Tests para el modelo PetReport"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.breed = Breed.objects.create(
            api_id="1",
            name="German Shepherd"
        )
        
        self.report = PetReport.objects.create(
            user=self.user,
            report_type='lost',
            pet_name='Rex',
            breed=self.breed,
            color='Negro',
            size='large',
            latitude=-33.8688,
            longitude=-51.2093,
            location_description='Parque Central',
            date_incident=datetime.now(),
            phone='+56912345678',
            email='user@example.com'
        )
    
    def test_report_creation(self):
        self.assertEqual(self.report.pet_name, 'Rex')
        self.assertEqual(self.report.report_type, 'lost')
        self.assertEqual(self.report.user, self.user)
    
    def test_report_id_generation(self):
        self.assertIsNotNone(self.report.report_id)
        self.assertTrue(self.report.report_id.startswith('lost-'))
    
    def test_report_str(self):
        self.assertIn('Rex', str(self.report))
        self.assertIn(self.report.report_id, str(self.report))


class MatchingServiceTests(TestCase):
    """Tests para el servicio de matching"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        self.breed = Breed.objects.create(
            api_id="1",
            name="Golden Retriever"
        )
        
        self.lost_report = PetReport.objects.create(
            user=self.user1,
            report_type='lost',
            pet_name='Buddy',
            breed=self.breed,
            color='Dorado',
            size='large',
            latitude=-33.8688,
            longitude=-51.2093,
            location_description='Zona norte',
            date_incident=datetime.now(),
            phone='+56912345678',
            email='user1@example.com'
        )
        
        self.found_report = PetReport.objects.create(
            user=self.user2,
            report_type='found',
            pet_name='Perro encontrado',
            breed=self.breed,
            color='Dorado claro',
            size='large',
            latitude=-33.8690,  # Muy cerca
            longitude=-51.2095,
            location_description='Zona norte',
            date_incident=datetime.now(),
            phone='+56912345679',
            email='user2@example.com'
        )
    
    def test_similarity_score_calculation(self):
        similarity = MatchingService.calculate_similarity_score(
            self.lost_report,
            self.found_report
        )
        
        self.assertIn('score', similarity)
        self.assertIn('reasons', similarity)
        self.assertGreater(similarity['score'], 50)
    
    def test_distance_calculation(self):
        distance = MatchingService._calculate_distance(
            -33.8688, -51.2093,
            -33.8690, -51.2095
        )
        
        self.assertGreater(distance, 0)
        self.assertLess(distance, 1)  # Menos de 1 km


class PetReportAPITests(APITestCase):
    """Tests para los endpoints de reportes"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.breed = Breed.objects.create(
            api_id="1",
            name="Poodle"
        )
        
        self.report = PetReport.objects.create(
            user=self.user,
            report_type='lost',
            pet_name='Fluffy',
            breed=self.breed,
            color='Blanco',
            size='small',
            latitude=-33.8688,
            longitude=-51.2093,
            location_description='Zona comercial',
            date_incident=datetime.now(),
            phone='+56912345678',
            email='user@example.com'
        )
    
    def test_list_reports(self):
        response = self.client.get('/api/v1/pets/reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_report_authenticated(self):
        self.client.force_authenticate(user=self.user)
        
        data = {
            'report_type': 'found',
            'pet_name': 'Doggo',
            'breed_id': self.breed.id,
            'color': 'Café',
            'size': 'medium',
            'latitude': -33.8688,
            'longitude': -51.2093,
            'location_description': 'Parque',
            'date_incident': datetime.now().isoformat(),
            'phone': '+56912345678',
            'email': 'user@example.com'
        }
        
        response = self.client.post('/api/v1/pets/reports/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_report_unauthenticated(self):
        data = {
            'report_type': 'found',
            'pet_name': 'Doggo',
            'breed_id': self.breed.id,
            'color': 'Café',
            'size': 'medium',
            'latitude': -33.8688,
            'longitude': -51.2093,
            'location_description': 'Parque',
            'date_incident': datetime.now().isoformat(),
            'phone': '+56912345678',
            'email': 'user@example.com'
        }
        
        response = self.client.post('/api/v1/pets/reports/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BreedAPITests(APITestCase):
    """Tests para los endpoints de razas"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.breed1 = Breed.objects.create(
            api_id="1",
            name="Bulldog"
        )
        
        self.breed2 = Breed.objects.create(
            api_id="2",
            name="Beagle"
        )
    
    def test_list_breeds(self):
        response = self.client.get('/api/v1/pets/breeds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_search_breeds(self):
        response = self.client.get('/api/v1/pets/breeds/search/?q=Bulldog')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
