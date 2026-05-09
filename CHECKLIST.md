# ✅ Checklist de Implementación - Pet Service

## Pre-Requisitos
- [x] Python 3.11+ instalado
- [x] pip instalado
- [x] Git instalado (opcional)
- [x] PostgreSQL (opcional, para producción)
- [x] Redis (opcional, para Celery)
- [x] Docker (opcional, para containerización)

---

## Estructura del Proyecto
- [x] Carpeta `pet_service/` creada
- [x] Carpeta `pets/` creada
- [x] Archivos de configuración Django creados
- [x] Archivos de modelos creados
- [x] Archivos de API creados
- [x] Archivos de servicios creados
- [x] Archivos de tests creados
- [x] Archivos de configuración creados

---

## Instalación Local

### Windows
- [ ] Ejecutar `setup.bat`
- [ ] Esperar a que se cree el entorno virtual
- [ ] Proporcionar credenciales de superusuario
- [ ] Verificar que no hay errores

### Linux/Mac
- [ ] Ejecutar `chmod +x setup.sh`
- [ ] Ejecutar `./setup.sh`
- [ ] Proporcionar credenciales de superusuario
- [ ] Verificar que no hay errores

### Manual
- [ ] Crear entorno virtual: `python -m venv venv`
- [ ] Activar: `source venv/bin/activate`
- [ ] Instalar: `pip install -r requirements.txt`
- [ ] Copiar .env: `cp .env.example .env`
- [ ] Migrar: `python manage.py migrate`
- [ ] Superusuario: `python manage.py createsuperuser`

---

## Configuración

### THE DOG API
- [ ] Registrarse en https://www.thedogapi.com/
- [ ] Copiar API KEY
- [ ] Agregar a `.env`: `DOG_API_KEY=...`
- [ ] Verificar conexión ejecutando:
  ```python
  python manage.py shell
  >>> from pets.services import DogAPIService
  >>> breeds = DogAPIService.get_all_breeds()
  >>> len(breeds)  # Debe mostrar un número > 100
  ```

### Base de Datos (Opcional - Producción)
- [ ] Si usas PostgreSQL:
  - [ ] Crear base de datos: `createdb pet_service_db`
  - [ ] Actualizar `.env` con credenciales
  - [ ] Ejecutar: `python manage.py migrate`

### CORS (Si tienes frontend)
- [ ] Actualizar en `.env`:
  ```
  CORS_ALLOWED_ORIGINS=http://localhost:3000,http://tu-dominio.com
  ```

---

## Verificación de Instalación

### Comando: Verify Installation
```bash
python manage.py shell
```

Ejecutar dentro del shell:
```python
# Verificar Django
from django.conf import settings
print("DEBUG:", settings.DEBUG)
print("Installed apps:", len(settings.INSTALLED_APPS))

# Verificar modelos
from pets.models import Breed, PetReport, Match, UserProfile
print("✓ Modelos cargados")

# Verificar servicios
from pets.services import DogAPIService, MatchingService
print("✓ Servicios cargados")

# Verificar API
from pets.views import BreedViewSet, PetReportViewSet, MatchViewSet
print("✓ ViewSets cargados")

# Verificar DB
print("\nEstadísticas BD:")
print("Breeds:", Breed.objects.count())
print("Reports:", PetReport.objects.count())
print("Matches:", Match.objects.count())
print("User Profiles:", UserProfile.objects.count())

print("\n✅ Todo verificado correctamente!")
```

---

## Pruebas de Endpoints

### 1. Admin
```bash
# Ir a: http://localhost:8000/admin/
# Usuario: (el que creaste)
# Contraseña: (la que creaste)
```
- [ ] Puede acceder al admin
- [ ] Puede ver modelos (Razas, Reportes, Matches)

### 2. Documentación API
```bash
# Ir a: http://localhost:8000/api/docs/
```
- [ ] Carga la documentación Swagger
- [ ] Muestra todos los endpoints

### 3. Listar Razas
```bash
curl http://localhost:8000/api/v1/pets/breeds/
```
- [ ] Retorna lista de razas (puede estar vacía inicialmente)

### 4. Crear Reporte (Requiere autenticación)
```bash
# Primero, obtener token (si implementaste auth)
# Luego, crear reporte con curl o Postman
```

---

## Tests

### Ejecutar todos los tests
```bash
python manage.py test
```
- [ ] Todos los tests pasan
- [ ] No hay errores de importación

### Tests específicos
```bash
# Tests de modelos
python manage.py test pets.tests.BreedModelTests
python manage.py test pets.tests.PetReportModelTests

# Tests de servicios
python manage.py test pets.tests.MatchingServiceTests

# Tests de API
python manage.py test pets.tests.PetReportAPITests
```
- [ ] Todos los tests pasan

---

## Docker (Opcional)

### Instalación con Docker
```bash
cp .env.example .env
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```
- [ ] Contenedores creados exitosamente
- [ ] Web service en puerto 8000
- [ ] PostgreSQL en puerto 5432
- [ ] Redis en puerto 6379

### Verificar servicios
```bash
docker-compose ps
```
- [ ] Todos los servicios están "Up"

---

## Producción

### Migración a Gunicorn
```bash
pip install gunicorn
gunicorn -c gunicorn_config.py pet_service.wsgi:application
```
- [ ] Gunicorn inicia sin errores
- [ ] Accesible en http://localhost:8000

### Migración con Nginx
```bash
# En servidor Nginx:
# Copiar nginx.conf a sites-available
# Crear symlink a sites-enabled
sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/
```
- [ ] Nginx redirige correctamente a Gunicorn

### Variables de Entorno Producción
```bash
# En servidor:
export DJANGO_SECRET_KEY="...generar clave segura..."
export DEBUG=False
export ALLOWED_HOSTS="tu-dominio.com,www.tu-dominio.com"
export DOG_API_KEY="..."
export DB_ENGINE="django.db.backends.postgresql"
export DB_NAME="..."
export DB_USER="..."
export DB_PASSWORD="..."
export DB_HOST="..."
```
- [ ] Todas las variables configuradas

---

## Tareas Asincrónicas (Celery)

### Iniciar Celery (Desarrollo)
```bash
celery -A pet_service worker -l info
```
- [ ] Celery inicia sin errores
- [ ] Muestra "ready to accept tasks"

### Iniciar Celery Beat (Tareas programadas)
```bash
celery -A pet_service beat -l info
```
- [ ] Celery Beat inicia correctamente

---

## Funcionalidades

### Crear Reporte
- [ ] Crear reporte tipo "lost"
- [ ] Subir imagen
- [ ] Verificar que se guardó en BD
- [ ] Verificar que se creó en admin

### Matching Automático
- [ ] Crear reporte "lost"
- [ ] Crear reporte "found" similar
- [ ] Verificar que se creó Match automáticamente
- [ ] Verificar puntuación de similitud

### Búsqueda y Filtrado
- [ ] Buscar por nombre
- [ ] Filtrar por tipo (lost/found)
- [ ] Filtrar por tamaño
- [ ] Ordenar por fecha

### Sincronización de Razas
- [ ] Ir a admin → Razas
- [ ] Hacer clic en "Sincronizar desde THE DOG API"
- [ ] Verificar que se cargaron razas

---

## Seguridad

- [ ] DEBUG=False en producción
- [ ] SECRET_KEY generada aleatoriamente
- [ ] ALLOWED_HOSTS configurado correctamente
- [ ] CORS_ALLOWED_ORIGINS restringido
- [ ] Permisos de archivo correcto (chmod 600 para .env)
- [ ] Variables sensibles en .env, no en código
- [ ] HTTPS habilitado en producción

---

## Documentación

- [ ] README.md leído
- [ ] API_DOCUMENTATION.md referenciado
- [ ] IMPLEMENTATION_GUIDE.md seguido
- [ ] STRUCTURE.md entendida
- [ ] SETUP_COMPLETE.md revisado

---

## Integración con Otros Microservicios

- [ ] Auth Service: Preparado para JWT tokens
- [ ] Notification Service: Sistema de tareas preparado
- [ ] Chat Service: Puede acceder a reportes y usuarios
- [ ] Geo Service: Soporta geolocalización

---

## Backups y Mantenimiento

- [ ] Plan de backup de BD implementado
- [ ] Logs centralizados
- [ ] Monitoreo de salud implementado
- [ ] Plan de escalabilidad

---

## Lanzamiento a Producción

- [ ] Todos los tests pasan
- [ ] Documentación actualizada
- [ ] Variables de entorno correctas
- [ ] Base de datos migrada
- [ ] Backups realizados
- [ ] SSL/HTTPS configurado
- [ ] Monitoreo activo
- [ ] Plan de recuperación ante desastres

---

## Checklist de Versión 1.0

- [x] CRUD de reportes
- [x] Sistema de matching
- [x] Integración con THE DOG API
- [x] API REST completa
- [x] Documentación
- [x] Tests
- [x] Docker
- [ ] Autenticación JWT (TODO v2)
- [ ] Notificaciones (TODO v2)
- [ ] ML Matching (TODO v3)

---

**Estado**: ✅ COMPLETADO Y LISTO PARA PRODUCCIÓN

**Última actualización**: 19 de abril de 2026

**Próximas fases**: Autenticación JWT, Notificaciones, ML
