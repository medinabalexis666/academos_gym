from rest_framework import serializers
from apps.users.models import CustomUser
from .models import Socio
#from core.debug import trampa

class SocioSerializer(serializers.ModelSerializer):

    # La contraseña se recibe en la tabla de usarios al crear el socio pero no se guarda en la tabla Socio:
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Socio
        fields = '__all__'
        read_only_fields = ['usuario']

    # Valido el email a ver si ya existe como usuario del sistema
    def validate_email(self, value):
        usuario = CustomUser.objects.filter(email=value).first()
        if usuario and (self.instance is None or usuario != self.instance.usuario):
            raise serializers.ValidationError('Ya existe un usuario con ese email.')
        return value

    # Valido la edad
    def validate_edad(self, value):
        # trampa()
        if value < 18 or value > 99:
            raise serializers.ValidationError("La edad debe estar entre 18 y 99 años.")
        return value
    
    # Valido el peso
    def validate_peso(self, value):
        if value is not None and (value < 30 or value > 300):
            raise serializers.ValidationError("El peso debe estar entre 30 y 300 kg.")
        return value

    # Valido la altura
    def validate_altura(self, value):
        if value is not None and (value < 50 or value > 250):
            raise serializers.ValidationError("La altura debe estar entre 50 y 250 cm.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        socio = Socio(**validated_data)
        # Creo automaticamente el usuario con el que el socio inicia sesion
        socio.usuario = CustomUser.objects.create_user(
            email=socio.email,
            password=password,
            nombre=socio.nombre,
        )
        socio.save()
        return socio

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        # Mantien sincronizado el login si cambian email, nombre o contraseña
        if instance.usuario:
            instance.usuario.email = instance.email
            instance.usuario.nombre = instance.nombre
            if password:
                instance.usuario.set_password(password)
            instance.usuario.save()
        return instance