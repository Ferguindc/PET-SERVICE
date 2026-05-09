from rest_framework import serializers
from .models import PetReport, PetReportImage, Breed, Match, UserProfile
from django.contrib.auth.models import User


class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = ['id', 'api_id', 'name', 'image_url', 'height_min', 'height_max', 'weight_min', 'weight_max']


class PetReportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetReportImage
        fields = ['id', 'image', 'uploaded_at', 'is_primary']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'phone', 'location', 'avatar', 'is_verified', 'reputation_score']


class UserSerializer(serializers.ModelSerializer):
    pet_profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'pet_profile']


class PetReportSerializer(serializers.ModelSerializer):
    """
    Serializer completo para PetReport con todas las relaciones.
    """
    breed = BreedSerializer(read_only=True)
    breed_id = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(),
        source='breed',
        write_only=True,
        required=False,
        allow_null=True
    )
    images = PetReportImageSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PetReport
        fields = [
            'id', 'report_id', 'user', 'report_type', 'pet_name', 'breed', 'breed_id',
            'breed_custom', 'color', 'size', 'distinguishing_features', 'collar_name',
            'latitude', 'longitude', 'location_description', 'date_incident',
            'created_at', 'updated_at', 'status', 'resolution_notes', 'phone', 'email',
            'is_verified', 'priority', 'images'
        ]
        read_only_fields = ['report_id', 'created_at', 'updated_at', 'user']


class PetReportCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para crear/actualizar reportes.
    """
    breed_id = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(),
        source='breed',
        required=False,
        allow_null=True
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = PetReport
        fields = [
            'report_type', 'pet_name', 'breed_id', 'breed_custom', 'color', 'size',
            'distinguishing_features', 'collar_name', 'latitude', 'longitude',
            'location_description', 'date_incident', 'phone', 'email', 'priority', 'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        validated_data['user'] = self.context['request'].user
        
        pet_report = PetReport.objects.create(**validated_data)
        
        # Crear imágenes
        for idx, image in enumerate(images):
            PetReportImage.objects.create(
                report=pet_report,
                image=image,
                is_primary=(idx == 0)
            )
        
        return pet_report

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar imágenes si se proporcionan
        if images is not None:
            instance.images.all().delete()
            for idx, image in enumerate(images):
                PetReportImage.objects.create(
                    report=instance,
                    image=image,
                    is_primary=(idx == 0)
                )
        
        return instance


class MatchSerializer(serializers.ModelSerializer):
    lost_report = PetReportSerializer(read_only=True)
    found_report = PetReportSerializer(read_only=True)
    
    class Meta:
        model = Match
        fields = [
            'id', 'lost_report', 'found_report', 'match_score',
            'match_reason', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PetReportListSerializer(serializers.ModelSerializer):
    """
    Serializer ligero para listados de reportes.
    """
    breed_name = serializers.CharField(source='breed.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = PetReport
        fields = [
            'id', 'report_id', 'report_type', 'pet_name', 'breed_name',
            'size', 'color', 'latitude', 'longitude', 'date_incident',
            'created_at', 'status', 'primary_image', 'user_name', 'priority'
        ]
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return primary.image.url
        return None
