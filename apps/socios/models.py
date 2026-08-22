import uuid
from django.db import models

class Socio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=60)
    apellido = models.CharField(max_length=60)
    edad = models.IntegerField()
    
    # Opciones para el campo Genero
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    email = models.EmailField(unique=True) 
    fecha_registro = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.nombre} {self.apellido} {self.email}"