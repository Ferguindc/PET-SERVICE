from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Permiso personalizado que permite a los propietarios de un objeto
    editarlo, y solo permite lectura a otros usuarios.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permitir métodos seguros (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        
        # Escribir permisos solo si el usuario es el propietario
        return obj.user == request.user


class IsAuthenticatedForCreate(BasePermission):
    """
    Permite crear objetos solo si el usuario está autenticado,
    pero permite lectura sin autenticación.
    """
    
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        return bool(request.user and request.user.is_authenticated)
