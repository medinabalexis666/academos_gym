import os
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Mensaje
from .serializers import MensajeSerializer


class BotGymView(APIView):
    serializer_class = MensajeSerializer

    def post(self, request):
        # 1. Se valida lo q manda el usuario
        serializer = MensajeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        texto_usuario = serializer.validated_data['mensaje']
        usuario = request.user

        # 2. Se guarda el mensaje del usuario en la BD
        Mensaje.objects.create(usuario=usuario, rol='user', contenido=texto_usuario)

        # 3. Recuperamos el historial reciente (Ej: últimos 10 mensajes)
        historial_bd = Mensaje.objects.filter(usuario=usuario).order_by('-timestamp')[:10]
        
        # Formateamos al estándar que exigen las IAs: [{"role": "user", "content": "..."}]
        historial_formateado = [
            {"role": msg.rol, "content": msg.contenido} 
            for msg in reversed(historial_bd) # Revertimos para que esté en orden cronológico
        ]

        # 4. Colocamos el RAG (Contexto propio del gimnasio) en el Prompt de Sistema
        prompt_sistema = {
            "role": "system", 
            "content": """
            Eres 'BotGym', asistente del gimnasio Academos. Sé muy breve (máximo 2 frases).

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
            2. Si preguntan sobre rutinas, usa tu conocimiento general.
            3. Responde SIEMPRE en español.
            """
        }
        historial_formateado.insert(0, prompt_sistema)

        # 5. Configuramos la petición según el entorno (Ollama o Groq)
        provider = os.getenv('AI_PROVIDER')
        if provider == 'groq':
            url = os.getenv('GROQ_URL')
            headers = {
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            }
            model = os.getenv('GROQ_MODEL')
            # AGREGA ESTAS DOS LÍNEAS PARA DEPURAR:
            print(f"+++ DEPURANDO URL: {url}")
            print(f"+++ DEPURANDO KEY (Primeros 10 chars): {os.getenv('GROQ_API_KEY')[:10]}")

        else: # Por defecto se usa Ollama
            url = os.getenv('OLLAMA_URL')
            headers = {"Content-Type": "application/json"}
            model = os.getenv('OLLAMA_MODEL')

        #print(f"+++ PROVEEDOR DETECTADO: {provider}")
        #print(f"+++ URL OLLAMA DETECTADA: {os.getenv('OLLAMA_URL')}")
        payload = {
            "model": model,
            "messages": historial_formateado
        }

        # 6. Hablar con la IA
        try:
            respuesta_ia = requests.post(url, json=payload, headers=headers, timeout=180)
            respuesta_ia.raise_for_status() # Si hay error 404, salta al except de abajo
            data = respuesta_ia.json()
            texto_ia = data['choices'][0]['message']['content']
            
        except requests.exceptions.HTTPError as e:
            # ESTO ES NUEVO: Imprimir lo que Groq nos respondió en el cuerpo del error
            print(f"+++ CUERPO DEL ERROR DE GROQ: {e.response.text}")
            texto_ia = f"Error con el servidor de IA: {str(e)}"
            
        except Exception as e:
            texto_ia = f"Error general de conexión: {str(e)}"
        '''try:
            respuesta_ia = requests.post(url, json=payload, headers=headers, timeout=180)
            respuesta_ia.raise_for_status() # Si hay error de conexión, explota aquí
            data = respuesta_ia.json()
            texto_ia = data['choices'][0]['message']['content']
        except Exception as e:
            texto_ia = f"Lo siento, mi cerebro está desconectado. Error: {str(e)}"
        '''
        # 7. Guardar la respuesta de la IA en la BD (Para la próxima vez)
        Mensaje.objects.create(usuario=usuario, rol='assistant', contenido=texto_ia)

        # 8. Devolver al usuario
        return Response({"respuesta": texto_ia}, status=status.HTTP_200_OK)