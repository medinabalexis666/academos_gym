import uuid
from django.db import models
from django.conf import settings

class Mensaje(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamos el mensaje con nuestro usuario personalizado
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='mensajes'
    )
    
    # ¿Quién habló? El usuario humano o el asistente (IA)
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