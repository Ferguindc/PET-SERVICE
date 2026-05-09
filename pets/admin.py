from django.contrib import admin
from .models import PetReport, PetReportImage, Breed, Match, UserProfile


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ['name', 'api_id', 'height_min', 'height_max', 'weight_min', 'weight_max', 'created_at']
    search_fields = ['name', 'api_id']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']


class PetReportImageInline(admin.TabularInline):
    model = PetReportImage
    extra = 1


@admin.register(PetReport)
class PetReportAdmin(admin.ModelAdmin):
    list_display = ['report_id', 'pet_name', 'report_type', 'status', 'user', 'priority', 'created_at']
    list_filter = ['report_type', 'status', 'size', 'is_verified', 'priority', 'created_at']
    search_fields = ['pet_name', 'user__username', 'report_id', 'location_description']
    readonly_fields = ['report_id', 'created_at', 'updated_at']
    inlines = [PetReportImageInline]
    fieldsets = (
        ('Información del Reporte', {
            'fields': ('report_id', 'user', 'report_type', 'status', 'is_verified', 'priority')
        }),
        ('Información de la Mascota', {
            'fields': ('pet_name', 'breed', 'breed_custom', 'color', 'size', 'collar_name')
        }),
        ('Características Distintivas', {
            'fields': ('distinguishing_features',)
        }),
        ('Ubicación', {
            'fields': ('latitude', 'longitude', 'location_description')
        }),
        ('Fechas', {
            'fields': ('date_incident', 'created_at', 'updated_at')
        }),
        ('Contacto', {
            'fields': ('phone', 'email')
        }),
        ('Resolución', {
            'fields': ('resolution_notes',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editando un objeto existente
            return self.readonly_fields + ['user']
        return self.readonly_fields


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'lost_report', 'found_report', 'match_score', 'status', 'created_at']
    list_filter = ['status', 'match_score', 'created_at']
    search_fields = ['lost_report__pet_name', 'found_report__pet_name']
    readonly_fields = ['created_at', 'updated_at', 'match_score', 'match_reason']
    fields = ['lost_report', 'found_report', 'match_score', 'match_reason', 'status', 'created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'location', 'is_verified', 'reputation_score', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'location']
    readonly_fields = ['created_at', 'updated_at']
