from rest_framework import serializers
from .models import Mensaje, Conversacion


class MensajeSerializer(serializers.Serializer):
    """Para recibir preguntas del usuario"""
    mensaje = serializers.CharField(max_length=2000)
    conversacion_id = serializers.UUIDField(required=False, allow_null=True)


class MensajeReadSerializer(serializers.ModelSerializer):
    """Para mostrar mensajes en el detalle de conversación"""
    class Meta:
        model = Mensaje
        fields = ['id', 'rol', 'contenido', 'timestamp']
        read_only_fields = fields


class ConversacionListSerializer(serializers.ModelSerializer):
    """Lista resumida de conversaciones"""
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)

    class Meta:
        model = Conversacion
        fields = ['id', 'titulo', 'usuario_nombre', 'usuario_email', 'created_at', 'updated_at']


class ConversacionDetailSerializer(serializers.ModelSerializer):
    """Detalle con todos los mensajes"""
    mensajes = MensajeReadSerializer(many=True, read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)

    class Meta:
        model = Conversacion
        fields = ['id', 'titulo', 'usuario_nombre', 'usuario_email', 'created_at', 'updated_at', 'mensajes']