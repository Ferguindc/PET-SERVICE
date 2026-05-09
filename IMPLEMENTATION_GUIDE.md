# 🎯 Guía de Implementación - Pet Service

## 📋 Descripción General

El **Pet Service** es un microservicio Django profesional para gestionar reportes de mascotas perdidas y encontradas. Implementa:

- ✅ Gestión completa de reportes con imágenes
- ✅ Integración con THE DOG API para razas
- ✅ Sistema inteligente de matching automático
- ✅ API REST completa con documentación
- ✅ Autenticación y permisos
- ✅ Filtrado y búsqueda avanzada
- ✅ Tareas asincrónicas con Celery
- ✅ Containerización con Docker

---

## 🚀 Primeros Pasos

### Opción 1: Instalación Local (Recomendado para desarrollo)

#### Windows
```cmd
# Desde la carpeta Pet service 2
setup.bat
```

#### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

#### Manual
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

### Opción 2: Instalación con Docker

```bash
# Copiar archivo .env
cp .env.example .env

# Construir e iniciar servicios
docker-compose up -d

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser
```

---

## ⚙️ Configuración Inicial

### 1. Configurar THE DOG API

1. Ir a https://www.thedogapi.com/
2. Registrarse y obtener la clave API
3. Agregar a `.env`:
```
DOG_API_KEY=your-api-key-here
```

4. Sincronizar razas:
```bash
python manage.py shell
>>> from pets.services import DogAPIService
>>> DogAPIService.get_all_breeds(force_refresh=True)
```

O acceder a: `/admin/` → Razas → "Sincronizar desde THE DOG API"

### 2. Configurar Base de Datos

**SQLite (Por defecto - desarrollo)**
```
# .env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

**PostgreSQL (Producción)**
```
# .env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pet_service_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### 3. Configurar CORS

Modificar en `.env`:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## 📊 Acceso a la Aplicación

### Desarrollo Local
- **Admin**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/v1/pets/
- **Documentación Swagger**: http://localhost:8000/api/docs/
- **Documentación ReDoc**: http://localhost:8000/api/redoc/

### Con Docker
- Todos los endpoints igual, servicios en contenedores

---

## 🔑 Características Principales

### 1. Gestión de Reportes

**Crear reporte con curl:**
```bash
curl -X POST http://localhost:8000/api/v1/pets/reports/ \
  -H "Authorization: Token your-token" \
  -F "report_type=lost" \
  -F "pet_name=Max" \
  -F "breed_id=22" \
  -F "color=Negro" \
  -F "size=large" \
  -F "latitude=-33.8688" \
  -F "longitude=-51.2093" \
  -F "location_description=Parque Central" \
  -F "date_incident=2024-01-15T10:00:00Z" \
  -F "phone=+56912345678" \
  -F "email=user@example.com" \
  -F "images=@photo.jpg"
```

### 2. Sistema de Matching

El sistema calcula automáticamente coincidencias considerando:
- **Raza**: Coincidencia exacta = 100%
- **Color**: Similitud textual
- **Tamaño**: Compatibilidad
- **Ubicación**: Proximidad geográfica (<5km)
- **Tiempo**: Cercanía temporal (<7 días)

**Obtener coincidencias:**
```bash
curl http://localhost:8000/api/v1/pets/reports/1/matches/ \
  -H "Authorization: Token your-token"
```

### 3. Filtrado y Búsqueda

```bash
# Mascotas perdidas grandes activas
curl "http://localhost:8000/api/v1/pets/reports/?report_type=lost&size=large&status=active"

# Buscar por nombre o raza
curl "http://localhost:8000/api/v1/pets/reports/?search=Labrador"

# Con paginación
curl "http://localhost:8000/api/v1/pets/reports/?page=1&page_size=50"
```

---

## 📱 Estructura de Datos

### PetReport (Reporte)
```python
{
    "report_type": "lost" | "found",
    "pet_name": "Nombre de la mascota",
    "breed": "Raza (ID)",
    "color": "Color o características",
    "size": "small | medium | large | giant",
    "latitude": -33.8688,
    "longitude": -51.2093,
    "location_description": "Descripción del lugar",
    "date_incident": "2024-01-15T10:00:00Z",
    "phone": "+56912345678",
    "email": "user@example.com",
    "distinguishing_features": "Características especiales",
    "collar_name": "Nombre en collar",
    "priority": 1-10,
    "images": [...]
}
```

---

## 🧪 Testing

### Ejecutar tests
```bash
python manage.py test
```

### Tests específicos
```bash
python manage.py test pets.tests.PetReportAPITests
python manage.py test pets.tests.MatchingServiceTests
```

---

## 📚 Documentación Completa

Ver `README.md` y `API_DOCUMENTATION.md` para:
- Todos los endpoints disponibles
- Parámetros de filtro
- Ejemplos de solicitud/respuesta
- Códigos de error
- Mejores prácticas

---

## 🔄 Tareas Asincrónicas (Celery)

### Iniciar Celery (desarrollo)
```bash
celery -A pet_service worker -l info
```

### Iniciar Celery Beat (tareas programadas)
```bash
celery -A pet_service beat -l info
```

### Tareas disponibles
- `sync_dog_breeds`: Sincronizar razas (Domingos 2 AM)
- `find_matches_for_report`: Encontrar coincidencias
- `send_match_notification`: Enviar notificaciones
- `cleanup_archived_reports`: Limpiar antiguos (Primer día mes 3 AM)

---

## 🚨 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "No such table"
```bash
python manage.py migrate
```

### Error: "Connection refused" (PostgreSQL)
- Verificar que PostgreSQL esté corriendo
- Verificar credenciales en .env
- Con Docker: `docker-compose up -d postgres`

### Error: "API request failed"
- Verificar conexión a internet
- Verificar clave API de THE DOG API
- Verificar en logs

---

## 📝 Próximos Pasos

1. **Autenticación avanzada**: Implementar JWT/OAuth2
2. **Notificaciones**: Integrar con Notification Service
3. **Machine Learning**: Mejorar matching con IA
4. **Búsqueda geoespacial**: Búsqueda por radio desde ubicación
5. **Social features**: Sistema de likes, comentarios, reputación
6. **Integración de mapas**: Mostrar ubicaciones en mapa
7. **Carga de imágenes mejorada**: Resize, compresión, validación

---

## 🤝 Integración con Otros Microservicios

### Con Auth Service
```python
# Validar tokens del Auth Service
# (Implementar en custom Authentication class)
```

### Con Notification Service
```python
# Enviar notificaciones de matches
POST /api/v1/notifications/send/
{
    "user_id": 1,
    "title": "¡Nueva coincidencia!",
    "message": "Se encontró una posible coincidencia..."
}
```

### Con Chat Service
```python
# Iniciar chat entre usuarios que confirmaron match
POST /api/v1/chats/start/
{
    "user1": 1,
    "user2": 2,
    "context": "match_id_123"
}
```

---

## ✨ Casos de Uso

### 1. Usuario encuentra mascota perdida
1. Crea reporte tipo "found"
2. Sistema detecta coincidencias automáticamente
3. Notificaciones enviadas a dueños de mascotas similares

### 2. Dueño reporta mascota perdida
1. Crea reporte tipo "lost"
2. Sistema compara con mascotas encontradas
3. Mostrar coincidencias en tiempo real

### 3. Confirmación de match
1. Usuario confirma coincidencia
2. Mascotas se unen
3. Chat abierto entre usuarios
4. Notificación enviada a ambos

---

## 📞 Soporte

Para problemas o preguntas:
- Revisar `README.md`
- Revisar `API_DOCUMENTATION.md`
- Revisar logs: `python manage.py runserver` o `docker-compose logs -f`
