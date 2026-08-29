from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# El Manager, Le dice a Django cómo crear usuarios y superusuarios
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) # Encripta la contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# 2. El Modelo: Nuestra tabla de usuarios
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    nombre = models.CharField(max_length=60, blank=True)
    is_active = models.BooleanField(default=True) # Para poder desactivar usuarios
    is_staff = models.BooleanField(default=False) 

    objects = CustomUserManager()

    # Se configura para q el email reemplace al username, estos seran los campos q se pediran cuando se cree el supr usuario
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre'] 

    def __str__(self):
        return self.email