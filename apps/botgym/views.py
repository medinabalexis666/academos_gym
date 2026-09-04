import os
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.utils import timezone
from datetime import timedelta
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

        '''
        Se controla la creacion o continuacion de la conversion, la cual tiene una
        duracion de 30 minutos.
        '''
        if conversacion_id:
            try:
                conversacion = Conversacion.objects.get(id=conversacion_id, usuario=usuario)
            except Conversacion.DoesNotExist:
                return Response(
                    {"error": "Conversación no encontrada."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            hace_30_min = timezone.now() - timedelta(minutes=30)
            conversacion_activa = Conversacion.objects.filter(
                usuario=usuario,
                updated_at__gte=hace_30_min
            ).order_by('-updated_at').first()

            if conversacion_activa:
                # Continuar la conversación existente
                conversacion = conversacion_activa
            else:
                # No hay sesión activa → crear nueva
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
        conversacion.save() 

        # Historial de esta conversación
        historial_bd = Mensaje.objects.filter(
            conversacion=conversacion
        ).order_by('timestamp')[:10]

        historial_formateado = [
            {"role": msg.rol, "content": msg.contenido}
            for msg in historial_bd
        ]

        datos_socio = ""
        # --- Datos de la persona que conversa ---
        # El nombre SIEMPRE se toma del usuario autenticado (JWT), nunca se le pregunta al bot.
        if hasattr(usuario, 'socio'):
            socio = usuario.socio
            nombre_persona = f"{socio.nombre} {socio.apellido}".strip()
        else:
            # Personal administrativo o superusuario: usamos el nombre de su cuenta
            nombre_persona = usuario.nombre.strip() or usuario.email

        datos_persona = f"""
            --- DATOS DE LA PERSONA QUE HABLA CONTIGO ---
            - Nombre: {nombre_persona}
            - Email: {usuario.email}"""

        if hasattr(usuario, 'socio'):
            socio = usuario.socio
            datos_persona += f"""
            - Edad: {socio.edad} años
            - Género: {socio.get_genero_display()}"""
            if socio.peso:
                datos_persona += f"\n- Peso: {socio.peso} kg"
            if socio.altura:
                datos_persona += f"\n- Altura: {socio.altura} cm"
            if socio.objetivo:
                datos_persona += f"\n- Objetivo: {socio.get_objetivo_display()}"
            if socio.nivel_actividad:
                datos_persona += f"\n- Nivel: {socio.get_nivel_actividad_display()}"
            if socio.condiciones_medicas:
                datos_persona += f"\n- Condiciones médicas: {socio.condiciones_medicas}"

        prompt_sistema = {
            "role": "system",
            "content": f"""
            Eres 'BotGym', asistente del gimnasio Academos. Sé muy breve (máximo 3 frases).

            {datos_persona}

            --- BASE DE CONOCIMIENTO DEL GIMNASIO (RAG) ---
            Horarios:
            - Lunes a Viernes: 6:00 AM a 10:00 PM
            - Sábados: 8:00 AM a 2:00 PM
            - Domingos: CERRADO
            
            Precios Membresías:
            - Básica: $30 USD
            - Premium (con clases): $50 USD
            - VIP (Personalizado): $70 USD

            --- EJERCICIOS O RUTINAS TRADICIONALES DE GIMNASIO POR GRUPO MUSCULAR ----

            [PECHO / CHEST]
            - Press de banca plano con barra o mancuernas
            - Press inclinado con mancuernas
            - Aperturas en polea o máquina (Cruces de polea)
            - Fondos en paralelas

            [ESPALDA / BACK]
            - Dominadas o Jalón al pecho en polea
            - Remo con barra o remo con mancuerna
            - Remo en máquina sentado (Gironda)
            - Pullover en polea alta

            [PIERNAS / LEGS]
            - Sentadillas libres con barra (Squats)
            - Prensa de piernas (Leg Press)
            - Extensiones de cuádriceps en máquina
            - Curl de piernas acostado o sentado (Femorales)
            - Zancadas con mancuernas (Lunges)
            - Elevación de talones en máquina (Gemelos)

            [HOMBROS / SHOULDERS]
            - Press militar con barra o mancuernas sentado
            - Elevaciones laterales con mancuernas
            - Pájaros con mancuernas (Hombro posterior)

            [BRAZOS / ARMS]
            - Curl de bíceps con barra o mancuernas
            - Curl de bíceps martillo
            - Extensión de tríceps en polea alta (con cuerda o barra)
            - Press francés para tríceps

            [ABDOMEN Y CORE / ABS]
            - Crunches abdominales en el suelo
            - Plancha isométrica
            - Elevaciones de piernas colgado

            --- RUTINAS CLÁSICAS Y COMUNES ---

            [RUTINA DE 3 DÍAS: CUERPO COMPLETO (FULL BODY)]
            - Ideal para: Principiantes o personas con poco tiempo.
            - Cómo se hace: Se entrena 3 días alternos (ej. Lunes, Miércoles, Viernes). En cada sesión se hace 1 ejercicio de pecho, 1 de espalda, 1 de pierna, 1 de hombro y 1 de brazo.

            [RUTINA DE 4 DÍAS: TORSO / PIERNA]
            - Ideal para: Nivel intermedio.
            - Cómo se hace: 
            * Lunes y Jueves: Solo ejercicios de Torso (Pecho, Espalda, Hombros, Brazos).
            * Martes y Viernes: Solo ejercicios de Pierna y Abdomen.

            [RUTINA DE 5 DÍAS: UN MÚSCULO POR DÍA (RUTINA WEIDER)]
            - Ideal para: La rutina más tradicional y famosa de los gimnasios.
            - Cómo se hace:
            * Lunes: Pecho
            * Martes: Espalda
            * Miércoles: Piernas
            * Jueves: Hombros
            * Viernes: Brazos (Bíceps y Tríceps)

            
            Métodos de pago: Solo efectivo o transferencia los primeros 5 días del mes.
            -----------------------------------------------
            
            REGLAS ESTRICTAS:
            1. Si preguntan por HORARIOS o PRECIOS, usa SOLO la info de arriba. NUNCA inventes.
            2. SIEMPRE saluda a la persona por su NOMBRE al inicio de tu respuesta. Ese nombre ya te lo di arriba: NUNCA lo preguntes ni pidas datos de registro.
            3. Usa los DATOS DE LA PERSONA (edad, peso, objetivo, nivel) para personalizar cuando existan.
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
        conversacion.save()  

        return Response({
            "respuesta": texto_ia,
            "conversacion_id": str(conversacion.id)
        }, status=status.HTTP_200_OK)


class MisConversacionesView(ListAPIView):
    """Lista conversaciones: el socio ve solo las suyas, el personal ve todas"""
    permission_classes = [IsAuthenticated]  # si esta autenticado puede conversar
    serializer_class = ConversacionListSerializer

    def get_queryset(self):
        usuario = self.request.user
        if hasattr(usuario, 'socio'):
            # Si es  socio, solo ve sus conversaciones
            return Conversacion.objects.filter(usuario=usuario).select_related('usuario').order_by('-updated_at')
        # Es usuario puede ver  todas las conversaciones (consulta de historiales)
        return Conversacion.objects.all().select_related('usuario').order_by('-updated_at')


class DetalleConversacionView(RetrieveAPIView):
    """Ver los mensajes de una conversación específica"""
    permission_classes = [IsAuthenticated]  
    serializer_class = ConversacionDetailSerializer

    def get_queryset(self):
        usuario = self.request.user
        if hasattr(usuario, 'socio'):
            return Conversacion.objects.filter(usuario=usuario).select_related('usuario')
        return Conversacion.objects.all().select_related('usuario')