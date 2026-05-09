# 🐕 Pet Service - Microservicio de Gestión de Mascotas

Pet Service es un microservicio Django diseñado para gestionar reportes de mascotas perdidas y encontradas. Facilita el registro de reportes con información detallada y realiza coincidencias automáticas entre mascotas perdidas y encontradas.

## ✨ Características

### 📋 Gestión de Reportes
- **Crear reportes** de mascotas perdidas y encontradas
- **Subir imágenes** de mascotas (múltiples imágenes por reporte)
- **Integración con THE DOG API** para razas validadas
- **Información detallada**: nombre, raza, color, tamaño, características distintivas
- **Geolocalización**: latitud, longitud y descripción de ubicación
- **Información de contacto**: teléfono y email del reportero

### 🔍 Sistema de Coincidencias (Matching)
- **Detección automática** de coincidencias entre reportes
- **Algoritmo inteligente** que considera:
  - Similitud de raza (30%)
  - Similitud de color (25%)
  - Compatibilidad de tamaño (20%)
  - Proximidad geográfica (15%)
  - Cercanía temporal (10%)
- **Puntuación de similitud** (0-100)
- **Confirmación y rechazo** de coincidencias por usuarios

### 👥 Gestión de Usuarios
- **Perfiles de usuario** con reputación
- **Verificación** de usuarios
- **Historial** de reportes del usuario

### 📊 Filtrado y Búsqueda
- Filtrar por tipo de reporte (perdido/encontrado)
- Filtrar por estado (activo/resuelto/archivado)
- Filtrar por tamaño, raza, ubicación
- Búsqueda de texto en nombre, raza, ubicación

### 📚 Documentación API
- **Swagger UI** en `/api/docs/`
- **ReDoc** en `/api/redoc/`

## 🏗️ Arquitectura

### Modelos de Datos

```
Breed
  - Información de razas desde THE DOG API
  - Dimensiones (altura, peso)

PetReport
  - Reporte de mascota perdida o encontrada
  - Información de contacto
  - Geolocalización
  - Imágenes

PetReportImage
  - Imágenes asociadas a reportes
  - Soporte para imagen principal

Match
  - Coincidencias entre reportes
  - Puntuación de similitud
  - Estado de la coincidencia

UserProfile
  - Extensión de perfil de usuario
  - Reputación y verificación
```

## 🚀 Instalación y Configuración

### Requisitos
- Python 3.11+
- PostgreSQL 13+
- Redis (opcional, para Celery)
- Docker y Docker Compose (opcional)

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd pet-service
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tu configuración
```

5. **Ejecutar migraciones**
```bash
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Cargar razas desde THE DOG API**
```bash
python manage.py shell
>>> from pets.services import DogAPIService
>>> DogAPIService.get_all_breeds(force_refresh=True)
```

8. **Iniciar servidor**
```bash
python manage.py runserver
```

### Instalación con Docker

```bash
# Copiar archivo de entorno
cp .env.example .env

# Construir y ejecutar contenedores
docker-compose up -d

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser
```

## 📡 API Endpoints

### Razas (Breeds)

```
GET    /api/v1/pets/breeds/                 # Listar todas las razas
GET    /api/v1/pets/breeds/{id}/            # Obtener detalles de una raza
GET    /api/v1/pets/breeds/search/?q=query  # Buscar razas
POST   /api/v1/pets/breeds/sync_from_api/   # Sincronizar desde THE DOG API (admin)
```

### Reportes (Reports)

```
GET    /api/v1/pets/reports/                     # Listar todos los reportes
POST   /api/v1/pets/reports/                     # Crear nuevo reporte
GET    /api/v1/pets/reports/{id}/                # Obtener detalles del reporte
PUT    /api/v1/pets/reports/{id}/                # Actualizar reporte
PATCH  /api/v1/pets/reports/{id}/                # Actualización parcial
DELETE /api/v1/pets/reports/{id}/                # Eliminar reporte

GET    /api/v1/pets/reports/my_reports/         # Mis reportes
GET    /api/v1/pets/reports/by_type/?type=lost  # Reportes por tipo
GET    /api/v1/pets/reports/{id}/matches/       # Encontrar coincidencias
POST   /api/v1/pets/reports/{id}/mark_resolved/ # Marcar como resuelto
POST   /api/v1/pets/reports/{id}/archive/       # Archivar reporte
```

### Coincidencias (Matches)

```
GET    /api/v1/pets/matches/                 # Listar coincidencias
GET    /api/v1/pets/matches/{id}/            # Obtener detalles
GET    /api/v1/pets/matches/my_matches/      # Mis coincidencias
POST   /api/v1/pets/matches/{id}/confirm/    # Confirmar coincidencia
POST   /api/v1/pets/matches/{id}/reject/     # Rechazar coincidencia
```

## 📋 Ejemplo de Uso

### Crear un Reporte

```bash
curl -X POST http://localhost:8000/api/v1/pets/reports/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "lost",
    "pet_name": "Max",
    "breed_id": 1,
    "color": "Negro y blanco",
    "size": "medium",
    "latitude": -33.8688,
    "longitude": -51.2093,
    "location_description": "Perdido en Parque Central",
    "date_incident": "2024-01-15T10:00:00Z",
    "phone": "+56912345678",
    "email": "user@example.com",
    "distinguishing_features": "Cicatriz en ojo izquierdo",
    "collar_name": "Max"
  }'
```

### Obtener Coincidencias

```bash
curl http://localhost:8000/api/v1/pets/reports/1/matches/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```
DJANGO_SECRET_KEY          # Clave secreta de Django
DEBUG                      # Modo desarrollo (True/False)
ALLOWED_HOSTS              # Hosts permitidos (separados por comas)

DB_ENGINE                  # Motor de base de datos
DB_NAME                    # Nombre de la base de datos
DB_USER                    # Usuario de base de datos
DB_PASSWORD                # Contraseña de base de datos
DB_HOST                    # Host de base de datos
DB_PORT                    # Puerto de base de datos

DOG_API_KEY                # Clave de THE DOG API

CORS_ALLOWED_ORIGINS       # Orígenes CORS permitidos

CELERY_BROKER_URL          # URL del broker de Celery
CELERY_RESULT_BACKEND      # Backend de resultados de Celery
```

### THE DOG API

1. Obtener clave API en https://www.thedogapi.com/
2. Agregar a variables de entorno: `DOG_API_KEY=your-key`
3. Sincronizar razas:
   ```bash
   python manage.py shell
   >>> from pets.services import DogAPIService
   >>> DogAPIService.get_all_breeds(force_refresh=True)
   ```

## 📊 Algoritmo de Matching

El sistema de coincidencias utiliza un algoritmo ponderado que considera múltiples factores:

1. **Raza (30%)**: Coincidencia exacta = 100%, diferentes = 30%
2. **Color (25%)**: Basado en similitud textual (0-100%)
3. **Tamaño (20%)**: Coincidencia exacta = 100%, adyacente = 70%, alejado = 30%
4. **Ubicación (15%)**: ≤5km = 100%, >5km = 0%
5. **Tiempo (10%)**: ≤7 días = 100%, >7 días = 0%

**Puntuación mínima para coincidencia**: 50/100

## 🛡️ Seguridad

- ✅ Autenticación basada en tokens (pendiente: implementar)
- ✅ Permisos de propietario para edición
- ✅ Validación de entrada
- ✅ CORS configurado
- ✅ Variables de entorno para datos sensibles

## 📈 Mejoras Futuras

- [ ] Autenticación con JWT/OAuth2
- [ ] Sistema de notificaciones
- [ ] Búsqueda geoespacial avanzada
- [ ] Machine Learning para matching
- [ ] Sistema de reputación y badges
- [ ] Integración con Google Maps
- [ ] Soporte para múltiples especies

## 🐛 Troubleshooting

### Error: "No such table: pets_pet_report"
```bash
python manage.py migrate
```

### Error: "THE DOG API connection failed"
- Verificar clave API en .env
- Verificar conexión a internet

### Error: "Port 5432 already in use"
```bash
docker-compose down
# O cambiar puerto en .env
```

## 📄 Licencia

Este proyecto es parte del sistema de mascotas perdidas y encontradas.

## 👥 Contacto

Para reportar problemas o sugerencias, contactar al equipo de desarrollo.
