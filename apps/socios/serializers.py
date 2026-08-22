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