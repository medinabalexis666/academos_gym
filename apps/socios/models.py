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

    peso = models.FloatField(
        null=True, 
        blank=True,
        help_text="Peso en kg"
    )
    altura = models.FloatField(
        null=True, 
        blank=True,
        help_text="Altura en cm"
    )
    
    OBJETIVO_CHOICES = [
        ('ganar_musculo', 'Ganar masa muscular'),
        ('perder_peso', 'Perder grasa'),
        ('mantenerse', 'Mantenimiento'),
        ('resistencia', 'Mejorar resistencia'),
        ('flexibilidad', 'Mejorar flexibilidad'),
        ('salud', 'Salud general'),
    ]
    objetivo = models.CharField(
        max_length=20, 
        choices=OBJETIVO_CHOICES,
        null=True,
        blank=True
    )
    
    NIVEL_CHOICES = [
        ('sedentario', 'Sedentario (poco o nada de ejercicio)'),
        ('principiante', 'Principiante (< 6 meses)'),
        ('intermedio', 'Intermedio (6 meses - 2 años)'),
        ('avanzado', 'Avanzado (> 2 años)'),
    ]
    nivel_actividad = models.CharField(
        max_length=15,
        choices=NIVEL_CHOICES,
        null=True,
        blank=True,
        default='principiante'
    )
    
    condiciones_medicas = models.TextField(
        blank=True,
        default='',
        help_text="Lesiones, condiciones médicas, alergias, etc."
    )


    def __str__(self):
        return f"{self.nombre} {self.apellido} {self.email}"