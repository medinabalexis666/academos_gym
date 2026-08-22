import os
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView  # ← AGREGAR
from .models import Mensaje, Conversacion
from .serializers import (
    MensajeSerializer,
    ConversacionListSerializer,
    ConversacionDetailSerializer
)


class BotGymView(APIView):
    serializer_class = MensajeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):

        # 1. Validar lo que manda el usuario
        serializer = MensajeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        texto_usuario = serializer.validated_data['mensaje']
        conversacion_id = serializer.validated_data.get('conversacion_id')
        usuario = request.user

        # Verificar que el usuario ES un socio
        if not hasattr(usuario, 'socio') or usuario.socio is None:
            return Response(
                {"error": "Acceso denegado. Su usuario no está registrado como socio del gimnasio."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener o crear la conversación
        if conversacion_id:
            try:
                conversacion = Conversacion.objects.get(id=conversacion_id, usuario=usuario)
            except Conversacion.DoesNotExist:
                return Response(
                    {"error": "Conversación no encontrada."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            titulo = texto_usuario[:50] + "..." if len(texto_usuario) > 50 else texto_usuario
            conversacion = Conversacion.objects.create(
                usuario=usuario,
                titulo=titulo
            )

        # Guardar mensaje del usuario
        Mensaje.objects.create(
            usuario=usuario,
            rol='user',
            contenido=texto_usuario,
            conversacion=conversacion
        )

        # Historial de ESTA conversación
        historial_bd = Mensaje.objects.filter(
            conversacion=conversacion
        ).order_by('timestamp')[:10]
        
        historial_formateado = [
            {"role": msg.rol, "content": msg.contenido} 
            for msg in historial_bd
        ]

        # Prompt de sistema
        # Obtener datos del socio
        socio = usuario.socio
        datos_socio = f"""
        - Nombre: {socio.nombre} {socio.apellido}
        - Email: {socio.email}
        - Edad: {socio.edad} años
        - Género: {socio.get_genero_display()}"""

        # Agregar campos opcionales solo si tienen valor
        if socio.peso:
            datos_socio += f"\n- Peso: {socio.peso} kg"
        if socio.altura:
            datos_socio += f"\n- Altura: {socio.altura} cm"
        if socio.objetivo:
            datos_socio += f"\n- Objetivo: {socio.get_objetivo_display()}"
        if socio.nivel_actividad:
            datos_socio += f"\n- Nivel de actividad: {socio.get_nivel_actividad_display()}"
        if socio.condiciones_medicas:
            datos_socio += f"\n- Condiciones médicas: {socio.condiciones_medicas}"

        prompt_sistema = {
            "role": "system", 
            "content": f"""
            Eres 'BotGym', asistente del gimnasio Academos. Sé muy breve (máximo 3 frases).

            --- DATOS DEL SOCIO QUE HABLA CONTIGO ---
            {datos_socio}

            --- BASE DE CONOCIMIENTO DEL GIMNASIO (RAG) ---
            Horarios:
            - Lunes a Viernes: 6:00 AM a 10:00 PM
            - Sábados: 8:00 AM a 2:00 PM
            - Domingos: CERRADO
            
            Precios Membresías:
            - Básica: $30 USD
            - Premium (con clases): $50 USD
            - VIP (Personalizado): $70 USD
            
            Métodos de pago: Solo efectivo o transferencia los primeros 5 días del mes.
            -----------------------------------------------
            
            REGLAS ESTRICTAS:
            1. Si preguntan por HORARIOS o PRECIOS, usa SOLO la info de arriba. NUNCA inventes.
            2. SIEMPRE saluda al socio por su NOMBRE al inicio de tu respuesta.
            3. Usa los DATOS DEL SOCIO (edad, peso, objetivo, nivel) para personalizar.
            4. Si tiene condiciones médicas, TEN CUIDADO al recomendar ejercicios.
            5. Si pregunta por rutinas, adapta a su OBJETIVO y NIVEL DE ACTIVIDAD.
            6. Responde SIEMPRE en español.
            """
        }

        historial_formateado.insert(0, prompt_sistema)

        # Configurar petición según entorno
        provider = os.getenv('AI_PROVIDER')
        if provider == 'groq':
            url = os.getenv('GROQ_URL')
            headers = {
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            }
            model = os.getenv('GROQ_MODEL')
        else:
            url = os.getenv('OLLAMA_URL')
            headers = {"Content-Type": "application/json"}
            model = os.getenv('OLLAMA_MODEL')

        payload = {
            "model": model,
            "messages": historial_formateado
        }

        # Hablar con la IA
        try:
            respuesta_ia = requests.post(url, json=payload, headers=headers, timeout=180)
            respuesta_ia.raise_for_status()
            data = respuesta_ia.json()
            texto_ia = data['choices'][0]['message']['content']
            
        except requests.exceptions.HTTPError as e:
            texto_ia = f"Error con el servidor de IA: {str(e)}"
        except Exception as e:
            texto_ia = f"Error general de conexión: {str(e)}"

        # Guardar respuesta de la IA
        Mensaje.objects.create(
            usuario=usuario,
            rol='assistant',
            contenido=texto_ia,
            conversacion=conversacion
        )

        return Response({
            "respuesta": texto_ia,
            "conversacion_id": str(conversacion.id)
        }, status=status.HTTP_200_OK)


class MisConversacionesView(ListAPIView):
    """Lista las conversaciones del socio autenticado"""
    permission_classes = [IsAuthenticated]
    serializer_class = ConversacionListSerializer

    def get_queryset(self):
        return Conversacion.objects.filter(usuario=self.request.user).order_by('-updated_at')


class DetalleConversacionView(RetrieveAPIView):
    """Ver los mensajes de una conversación específica"""
    permission_classes = [IsAuthenticated]
    serializer_class = ConversacionDetailSerializer

    def get_queryset(self):
        return Conversacion.objects.filter(usuario=self.request.user)