from rest_framework import serializers
from .models import Socio
#from core.debug import trampa

class SocioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Socio
        fields = '__all__'

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