from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Socio
#from core.debug import trampa

User = get_user_model()

class SocioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Socio
        exclude = ['usuario']  # No aparece en la respuesta, es un id interno q identifica al registro en la tabla

    # Validando la edad
    def validate_edad(self, value):
        # trampa()
        if value < 10 or value > 99:
            raise serializers.ValidationError("La edad debe estar entre 10 y 99 años.")
        return value

    def validate_peso(self, value):
        if value is not None and (value < 20 or value > 300):
            raise serializers.ValidationError("El peso debe estar entre 20 y 300 kg.")
        return value

    def validate_altura(self, value):
        if value is not None and (value < 50 or value > 250):
            raise serializers.ValidationError("La altura debe estar entre 50 y 250 cm.")
        return value
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        
        # Crear el usuario con el email del socio
        if password:
            usuario = User.objects.create_user(
                email=validated_data['email'],
                password=password,
                nombre=validated_data.get('nombre', '')
            )
            validated_data['usuario'] = usuario
        
        return super().create(validated_data)