from rest_framework import serializers

class MensajeSerializer(serializers.Serializer):
    mensaje = serializers.CharField(max_length=2000)