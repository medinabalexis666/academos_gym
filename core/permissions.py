from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """Solo permite el acceso al superusuario."""
    message = 'Solo el superusuario puede realizar esta acción.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class EsPersonal(BasePermission):
    """Permite el acceso a los usuarios del gimnasio (excluye a los socios)."""
    message = 'Los socios no tienen acceso a esta función.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not hasattr(request.user, 'socio')
        )