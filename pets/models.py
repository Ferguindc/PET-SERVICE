from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class Breed(models.Model):
    """
    Modelo para razas de perros obtenidas de THE DOG API.
    Se crea una caché local para optimizar búsquedas.
    """
    api_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)
    height_min = models.FloatField(blank=True, null=True)
    height_max = models.FloatField(blank=True, null=True)
    weight_min = models.FloatField(blank=True, null=True)
    weight_max = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        db_table = 'pets_breed'
        verbose_name = 'Raza'
        verbose_name_plural = 'Razas'

    def __str__(self):
        return self.name


class PetReport(models.Model):
    """
    Modelo principal para reportes de mascotas perdidas y encontradas.
    """
    REPORT_STATUS_CHOICES = [
        ('active', 'Activo'),
        ('resolved', 'Resuelto'),
        ('archived', 'Archivado'),
    ]
    
    REPORT_TYPE_CHOICES = [
        ('lost', 'Perdido'),
        ('found', 'Encontrado'),
    ]
    
    SIZE_CHOICES = [
        ('small', 'Pequeño (0-10 kg)'),
        ('medium', 'Mediano (10-25 kg)'),
        ('large', 'Grande (25-50 kg)'),
        ('giant', 'Gigante (>50 kg)'),
    ]
    
    # Información básica
    report_id = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pet_reports')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)
    
    # Información de la mascota
    pet_name = models.CharField(max_length=100, help_text="Nombre de la mascota")
    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True, blank=True)
    breed_custom = models.CharField(max_length=255, blank=True, help_text="Raza personalizada si no está en la lista")
    color = models.CharField(max_length=100, help_text="Color o características físicas")
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    
    # Características distintivas
    distinguishing_features = models.TextField(blank=True, help_text="Cicatrices, manchas, collares, etc.")
    collar_name = models.CharField(max_length=255, blank=True, help_text="Nombre en collar (si tiene)")
    
    # Ubicación
    latitude = models.FloatField()
    longitude = models.FloatField()
    location_description = models.TextField(help_text="Descripción de dónde fue visto/encontrado")
    
    # Fechas
    date_incident = models.DateTimeField(help_text="Fecha y hora del incidente")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Estado
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='active')
    resolution_notes = models.TextField(blank=True, help_text="Notas sobre cómo se resolvió")
    
    # Contacto
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Metadatos
    is_verified = models.BooleanField(default=False, help_text="Verificado por administrador")
    priority = models.IntegerField(default=1, validators=[MinValueValidator(1)], help_text="Prioridad para matching (1-10)")
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'pets_pet_report'
        verbose_name = 'Reporte de Mascota'
        verbose_name_plural = 'Reportes de Mascotas'
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.pet_name} ({self.report_id})"

    def save(self, *args, **kwargs):
        if not self.report_id:
            import uuid
            from django.utils.text import slugify
            self.report_id = f"{self.report_type}-{slugify(self.pet_name)}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class PetReportImage(models.Model):
    """
    Modelo para almacenar múltiples imágenes por reporte.
    """
    report = models.ForeignKey(PetReport, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='pet_reports/%Y/%m/%d/', help_text="Foto de la mascota")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False, help_text="Imagen principal del reporte")
    
    class Meta:
        ordering = ['-is_primary', '-uploaded_at']
        db_table = 'pets_pet_report_image'
        verbose_name = 'Imagen de Reporte'
        verbose_name_plural = 'Imágenes de Reportes'

    def __str__(self):
        return f"Image - {self.report.pet_name}"


class Match(models.Model):
    """
    Modelo para rastrear coincidencias entre reportes.
    Se utiliza para el Match Service.
    """
    MATCH_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('rejected', 'Rechazado'),
        ('resolved', 'Resuelto'),
    ]
    
    lost_report = models.ForeignKey(
        PetReport,
        on_delete=models.CASCADE,
        related_name='matches_as_lost'
    )
    found_report = models.ForeignKey(
        PetReport,
        on_delete=models.CASCADE,
        related_name='matches_as_found'
    )
    
    match_score = models.FloatField(
        validators=[MinValueValidator(0), ],
        help_text="Puntuación de similitud (0-100)"
    )
    match_reason = models.TextField(help_text="Razones de la coincidencia")
    
    status = models.CharField(max_length=20, choices=MATCH_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-match_score']
        db_table = 'pets_match'
        verbose_name = 'Coincidencia'
        verbose_name_plural = 'Coincidencias'
        unique_together = ('lost_report', 'found_report')

    def __str__(self):
        return f"Match: {self.lost_report.pet_name} <-> {self.found_report.pet_name}"


class UserProfile(models.Model):
    """
    Extensión del perfil de usuario con información adicional.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pet_profile')
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='profiles/%Y/%m/%d/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    reputation_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pets_user_profile'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'

    def __str__(self):
        return f"Perfil: {self.user.get_full_name() or self.user.username}"
