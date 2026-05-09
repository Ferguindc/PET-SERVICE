# 📂 Estructura del Proyecto - Pet Service

```
pet-service/
├── pet_service/                    # Configuración principal del proyecto Django
│   ├── __init__.py
│   ├── settings.py                 # Configuración de Django
│   ├── urls.py                     # URLs principales
│   ├── wsgi.py                     # WSGI para producción
│   ├── asgi.py                     # ASGI para async
│   └── celery.py                   # Configuración de Celery
│
├── pets/                           # Aplicación principal
│   ├── migrations/                 # Migraciones de base de datos
│   ├── __init__.py
│   ├── admin.py                    # Configuración de admin de Django
│   ├── apps.py                     # Configuración de la app
│   ├── models.py                   # Modelos de datos
│   │   ├── Breed                   # Razas de perros
│   │   ├── PetReport               # Reportes de mascotas
│   │   ├── PetReportImage          # Imágenes de reportes
│   │   ├── Match                   # Coincidencias
│   │   └── UserProfile             # Perfiles de usuario
│   │
│   ├── serializers.py              # Serializadores REST
│   │   ├── BreedSerializer
│   │   ├── PetReportSerializer
│   │   ├── MatchSerializer
│   │   └── ...
│   │
│   ├── views.py                    # ViewSets y endpoints
│   │   ├── BreedViewSet
│   │   ├── PetReportViewSet
│   │   └── MatchViewSet
│   │
│   ├── services.py                 # Lógica de negocio
│   │   ├── DogAPIService          # Integración con THE DOG API
│   │   └── MatchingService         # Algoritmo de matching
│   │
│   ├── permissions.py              # Permisos personalizados
│   ├── urls.py                     # URLs de la app
│   ├── tasks.py                    # Tareas de Celery
│   ├── signals.py                  # Señales de Django
│   ├── celery_config.py            # Configuración de Celery Beat
│   └── tests.py                    # Tests unitarios
│
├── templates/                      # Templates HTML (si es necesario)
│
├── media/                          # Archivos subidos (imágenes)
│   └── pet_reports/
│       └── %Y/%m/%d/
│
├── staticfiles/                    # Archivos estáticos compilados
│
├── manage.py                       # Comando principal de Django
├── requirements.txt                # Dependencias de Python
├── .env.example                    # Ejemplo de variables de entorno
├── .env                            # Variables de entorno (LOCAL)
│
├── Dockerfile                      # Para containerizar con Docker
├── docker-compose.yml              # Orquestación de contenedores
│
├── gunicorn_config.py              # Configuración de Gunicorn
├── nginx.conf                      # Configuración de Nginx
│
├── pytest.ini                      # Configuración de pytest
│
├── README.md                       # Documentación principal
├── API_DOCUMENTATION.md            # Documentación de API
├── IMPLEMENTATION_GUIDE.md         # Guía de implementación
├── STRUCTURE.md                    # Este archivo
│
├── setup.sh                        # Script de instalación (Linux/Mac)
├── setup.bat                       # Script de instalación (Windows)
│
└── .gitignore                      # Archivos a ignorar en Git
```

---

## 📖 Descripción de Archivos Clave

### Configuración de Django

- **settings.py**: Configuración central (BD, apps, middleware, etc.)
- **urls.py**: Enrutamiento de URLs
- **wsgi.py**: Punto de entrada WSGI para servidores como Gunicorn
- **asgi.py**: Punto de entrada ASGI para aplicaciones async

### Aplicación `pets`

- **models.py**: Define la estructura de datos
- **serializers.py**: Convierte modelos a JSON y viceversa
- **views.py**: Lógica de los endpoints API
- **services.py**: Lógica de negocio compleja
- **permissions.py**: Control de acceso basado en roles
- **tasks.py**: Tareas asincrónicas con Celery
- **signals.py**: Acciones automáticas en eventos de BD

### Docker

- **Dockerfile**: Instrucciones para crear imagen Docker
- **docker-compose.yml**: Orquestación de servicios (Web, DB, Redis, etc.)

### Configuración de Servidor

- **gunicorn_config.py**: Configuración para servidor de aplicación
- **nginx.conf**: Configuración para servidor web

---

## 🔄 Flujo de Datos

### 1. Creación de Reporte
```
Cliente HTTP
    ↓
REST API (views.py)
    ↓
Serializer (serializers.py)
    ↓
Model (models.py)
    ↓
Base de Datos
    ↓
Signal post_save (signals.py)
    ↓
Task: find_matches (Celery)
    ↓
MatchingService (services.py)
    ↓
Match created en BD
    ↓
Task: send_notification (Celery)
```

### 2. Búsqueda de Coincidencias
```
GET /api/reports/1/matches/
    ↓
MatchingService.find_matches()
    ↓
Consultar BD (reportes opuestos)
    ↓
Calcular similitud (algoritmo)
    ↓
Retornar resultados JSON
```

---

## 🗄️ Base de Datos

### Tablas Principales

```
pets_breed
├── id (PK)
├── api_id (Unique)
├── name
├── image_url
├── height_min, height_max
├── weight_min, weight_max
└── created_at, updated_at

pets_pet_report
├── id (PK)
├── report_id (Unique)
├── user_id (FK)
├── report_type (lost/found)
├── pet_name
├── breed_id (FK)
├── breed_custom
├── color, size
├── latitude, longitude
├── location_description
├── date_incident
├── phone, email
├── distinguishing_features
├── collar_name
├── status (active/resolved/archived)
├── is_verified
├── priority
├── created_at, updated_at
└── indexes: (report_type, status), (lat, lon), (user, status)

pets_pet_report_image
├── id (PK)
├── report_id (FK)
├── image
├── uploaded_at
└── is_primary

pets_match
├── id (PK)
├── lost_report_id (FK)
├── found_report_id (FK)
├── match_score
├── match_reason
├── status (pending/confirmed/rejected/resolved)
├── created_at, updated_at
└── unique: (lost_report, found_report)

pets_user_profile
├── id (PK)
├── user_id (OneToOne FK)
├── phone, location
├── avatar
├── is_verified
├── reputation_score
└── created_at, updated_at

auth_user (Django built-in)
├── id (PK)
├── username
├── email
├── password_hash
└── ...
```

---

## 🔌 Endpoints API

```
/api/v1/pets/breeds/
├── GET     /              # Listar razas
├── GET     /{id}/         # Obtener raza
├── GET     /search/       # Buscar razas
└── POST    /sync_from_api/# Sincronizar con THE DOG API

/api/v1/pets/reports/
├── GET     /              # Listar reportes
├── POST    /              # Crear reporte
├── GET     /{id}/         # Obtener reporte
├── PUT     /{id}/         # Actualizar reporte
├── PATCH   /{id}/         # Actualización parcial
├── DELETE  /{id}/         # Eliminar reporte
├── GET     /my_reports/   # Mis reportes
├── GET     /by_type/      # Reportes por tipo
├── GET     /{id}/matches/ # Coincidencias
├── POST    /{id}/mark_resolved/  # Marcar resuelto
└── POST    /{id}/archive/ # Archivar

/api/v1/pets/matches/
├── GET     /              # Listar coincidencias
├── GET     /{id}/         # Obtener coincidencia
├── GET     /my_matches/   # Mis coincidencias
├── POST    /{id}/confirm/ # Confirmar coincidencia
└── POST    /{id}/reject/  # Rechazar coincidencia
```

---

## 🚀 Procesos en Background (Celery)

- `sync_dog_breeds`: Sincronizar razas (Semanal)
- `find_matches_for_report`: Encontrar coincidencias (Inmediato)
- `send_match_notification`: Notificaciones (Inmediato)
- `cleanup_archived_reports`: Limpieza (Mensual)

---

## 🔐 Autenticación y Permisos

- **IsOwnerOrReadOnly**: Propietario puede editar
- **IsAuthenticatedForCreate**: Autenticado para crear

---

## 📊 Algoritmo de Matching

Peso total = 100%
- Raza: 30%
- Color: 25%
- Tamaño: 20%
- Ubicación: 15%
- Tiempo: 10%

Puntuación mínima para match: 50/100

---

## 🎯 Casos de Extensión

### Para agregar nueva funcionalidad:

1. **Model**: Agregar en `models.py`
2. **Serializer**: Crear en `serializers.py`
3. **View**: Crear ViewSet en `views.py`
4. **URL**: Registrar en `urls.py`
5. **Admin**: Registrar en `admin.py` (si es necesario)
6. **Tests**: Agregar en `tests.py`
7. **Migrations**: Ejecutar `python manage.py makemigrations`
