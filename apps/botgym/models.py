import uuid
from django.db import models
from django.conf import settings

class Conversacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='conversaciones'
    )
    titulo = models.CharField(max_length=100, blank=True, default='Conversación')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.usuario.email}"

class Mensaje(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamos el mensaje con nuestro usuario personalizado
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='mensajes'
    )
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mensajes'
    )

    ROL_CHOICES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente (IA)'),
    ]
    rol = models.CharField(max_length=10, choices=ROL_CHOICES)
    
    # El texto del mensaje
    contenido = models.TextField()
    
    # Cuándo se dijo
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.rol}] {self.usuario.email}: {self.contenido[:30]}..."