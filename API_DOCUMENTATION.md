# 📚 Documentación de API - Pet Service

## Base URL
```
http://localhost:8000/api/v1/pets/
```

## Autenticación
Los endpoints protegidos requieren un token de autenticación. Incluir en el header:
```
Authorization: Token YOUR_AUTH_TOKEN
```

## Respuestas

### Formato exitoso (2xx)
```json
{
  "id": 1,
  "data": {...}
}
```

### Formato de error (4xx, 5xx)
```json
{
  "detail": "Descripción del error",
  "error_code": "ERROR_CODE"
}
```

---

## 🐶 Razas (Breeds)

### Listar todas las razas
```
GET /breeds/
```

**Parámetros de query:**
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (default: 20, max: 100)
- `search`: Buscar por nombre
- `ordering`: Ordenar por campo (ej: `name`, `-created_at`)

**Respuesta:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/pets/breeds/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "api_id": "1",
      "name": "Labrador Retriever",
      "image_url": "https://...",
      "height_min": 55.0,
      "height_max": 57.0,
      "weight_min": 25.0,
      "weight_max": 36.0
    }
  ]
}
```

### Obtener detalles de una raza
```
GET /breeds/{id}/
```

**Respuesta:**
```json
{
  "id": 1,
  "api_id": "1",
  "name": "Labrador Retriever",
  "image_url": "https://...",
  "height_min": 55.0,
  "height_max": 57.0,
  "weight_min": 25.0,
  "weight_max": 36.0
}
```

### Buscar razas
```
GET /breeds/search/?q=Golden
```

**Respuesta:**
```json
{
  "results": [
    {
      "id": 84,
      "api_id": "84",
      "name": "Golden Retriever",
      "image_url": "https://..."
    }
  ]
}
```

### Sincronizar razas desde THE DOG API
```
POST /breeds/sync_from_api/
```

**Permisos:** Solo administradores

**Respuesta:**
```json
{
  "message": "Se sincronizaron 200 razas correctamente.",
  "count": 200
}
```

---

## 🐕 Reportes (Reports)

### Listar todos los reportes
```
GET /reports/
```

**Parámetros de filtro:**
- `report_type`: `lost` o `found`
- `status`: `active`, `resolved`, `archived`
- `size`: `small`, `medium`, `large`, `giant`
- `breed`: ID de la raza
- `priority__gte`: Prioridad mínima
- `priority__lte`: Prioridad máxima
- `date_incident__gte`: Fecha mínima
- `date_incident__lte`: Fecha máxima

**Parámetros de búsqueda:**
- `search`: Busca en nombre, raza, ubicación y color

**Ejemplo:**
```
GET /reports/?report_type=lost&status=active&search=Max
```

**Respuesta:**
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/v1/pets/reports/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "report_id": "lost-max-a1b2c3d4",
      "report_type": "lost",
      "pet_name": "Max",
      "breed_name": "German Shepherd",
      "size": "large",
      "color": "Negro",
      "latitude": -33.8688,
      "longitude": -51.2093,
      "date_incident": "2024-01-15T10:00:00Z",
      "created_at": "2024-01-15T12:30:00Z",
      "status": "active",
      "primary_image": "https://example.com/media/pet_reports/2024/01/15/image.jpg",
      "user_name": "Juan Pérez",
      "priority": 5
    }
  ]
}
```

### Obtener detalles de un reporte
```
GET /reports/{id}/
```

**Respuesta:**
```json
{
  "id": 1,
  "report_id": "lost-max-a1b2c3d4",
  "user": {
    "id": 1,
    "username": "juanperez",
    "email": "juan@example.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "pet_profile": {
      "id": 1,
      "phone": "+56912345678",
      "location": "Santiago",
      "is_verified": true,
      "reputation_score": 10
    }
  },
  "report_type": "lost",
  "pet_name": "Max",
  "breed": {
    "id": 1,
    "api_id": "22",
    "name": "German Shepherd"
  },
  "breed_custom": "",
  "color": "Negro",
  "size": "large",
  "distinguishing_features": "Cicatriz en ojo izquierdo",
  "collar_name": "Max",
  "latitude": -33.8688,
  "longitude": -51.2093,
  "location_description": "Perdido en Parque Central",
  "date_incident": "2024-01-15T10:00:00Z",
  "created_at": "2024-01-15T12:30:00Z",
  "updated_at": "2024-01-15T12:30:00Z",
  "status": "active",
  "resolution_notes": "",
  "phone": "+56912345678",
  "email": "juan@example.com",
  "is_verified": false,
  "priority": 5,
  "images": [
    {
      "id": 1,
      "image": "https://example.com/media/pet_reports/2024/01/15/image.jpg",
      "uploaded_at": "2024-01-15T12:30:00Z",
      "is_primary": true
    }
  ]
}
```

### Crear un nuevo reporte
```
POST /reports/
```

**Headers requeridos:**
```
Authorization: Token YOUR_AUTH_TOKEN
Content-Type: multipart/form-data
```

**Parámetros (multipart/form-data):**
- `report_type` (required): `lost` o `found`
- `pet_name` (required): Nombre de la mascota
- `breed_id` (optional): ID de la raza
- `breed_custom` (optional): Raza personalizada si no está en la lista
- `color` (required): Color o características físicas
- `size` (required): Tamaño (small, medium, large, giant)
- `distinguishing_features` (optional): Cicatrices, manchas, etc.
- `collar_name` (optional): Nombre en collar
- `latitude` (required): Latitud
- `longitude` (required): Longitud
- `location_description` (required): Descripción de ubicación
- `date_incident` (required): Fecha/hora del incidente (ISO 8601)
- `phone` (required): Teléfono
- `email` (required): Email
- `priority` (optional): Prioridad 1-10 (default: 1)
- `images` (optional): Array de imágenes

**Ejemplo con curl:**
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
  -F "priority=5" \
  -F "images=@photo1.jpg" \
  -F "images=@photo2.jpg"
```

### Actualizar un reporte
```
PUT /reports/{id}/
PATCH /reports/{id}/
```

**Permisos:** Solo el propietario

**Parámetros:** Mismo que creación, pero todos opcionales

### Eliminar un reporte
```
DELETE /reports/{id}/
```

**Permisos:** Solo el propietario

### Mis reportes
```
GET /reports/my_reports/
```

**Autenticación:** Requerida

**Respuesta:** Lista de reportes del usuario autenticado

### Reportes por tipo
```
GET /reports/by_type/?type=lost
GET /reports/by_type/?type=found
```

**Parámetros:**
- `type` (required): `lost` o `found`

### Encontrar coincidencias
```
GET /reports/{id}/matches/
```

**Respuesta:**
```json
{
  "report_id": "lost-max-a1b2c3d4",
  "matches_found": 2,
  "matches": [
    {
      "report_id": "found-perro-b2c3d4e5",
      "pet_name": "Perro encontrado",
      "score": 87.5,
      "reasons": [
        "Raza coincide exactamente",
        "Color muy similar",
        "Muy cerca geográficamente (0.3 km)",
        "Reportes cercanos en tiempo (1 días)"
      ],
      "url": "/api/v1/pets/reports/2/"
    }
  ]
}
```

### Marcar reporte como resuelto
```
POST /reports/{id}/mark_resolved/
```

**Body (optional):**
```json
{
  "resolution_notes": "Se encontró la mascota en el refugio local"
}
```

**Permisos:** Solo el propietario o administrador

### Archivar un reporte
```
POST /reports/{id}/archive/
```

**Permisos:** Solo el propietario o administrador

---

## 🔍 Coincidencias (Matches)

### Listar coincidencias
```
GET /matches/
```

**Parámetros de filtro:**
- `status`: `pending`, `confirmed`, `rejected`, `resolved`
- `lost_report`: ID del reporte perdido
- `found_report`: ID del reporte encontrado

**Respuesta:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "lost_report": {...},
      "found_report": {...},
      "match_score": 87.5,
      "match_reason": "Raza coincide...",
      "status": "pending",
      "created_at": "2024-01-15T14:00:00Z",
      "updated_at": "2024-01-15T14:00:00Z"
    }
  ]
}
```

### Obtener detalles de una coincidencia
```
GET /matches/{id}/
```

### Mis coincidencias
```
GET /matches/my_matches/
```

**Autenticación:** Requerida

### Confirmar coincidencia
```
POST /matches/{id}/confirm/
```

**Permisos:** Propietario de uno de los reportes

**Respuesta:**
```json
{
  "message": "Coincidencia confirmada.",
  "match": {...}
}
```

### Rechazar coincidencia
```
POST /matches/{id}/reject/
```

**Permisos:** Propietario de uno de los reportes

---

## 📊 Filtros y Búsqueda

### Ejemplo: Buscar mascotas perdidas grandes de raza Labrador
```
GET /reports/?report_type=lost&size=large&breed=1&search=Labrador
```

### Ejemplo: Mascotas encontradas en los últimos 7 días
```
GET /reports/?report_type=found&status=active&date_incident__gte=2024-01-08
```

### Ordenamiento
```
GET /reports/?ordering=-priority,created_at
GET /reports/?ordering=date_incident
```

---

## ❌ Códigos de Error

| Código | Significado |
|--------|------------|
| 400 | Solicitud inválida |
| 401 | No autenticado |
| 403 | No autorizado (sin permisos) |
| 404 | Recurso no encontrado |
| 500 | Error del servidor |

---

## 🔐 Límites de Tasa (Rate Limiting)

Pendiente de implementación. Por ahora sin límites.

---

## 📝 Notas

- Las imágenes se cargan en formato multipart/form-data
- Las fechas se usan en formato ISO 8601
- La puntuación de coincidencia va de 0 a 100
- El matching se calcula automáticamente cuando se crea un reporte
