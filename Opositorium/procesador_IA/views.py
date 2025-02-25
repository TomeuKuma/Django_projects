import os
import time
import json
import datetime
from openai import OpenAI
from dotenv import load_dotenv
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from boib_scraper.models import AnuncioBoib
from .models import AnuncioBoibProcesado
from django.shortcuts import render

# Cargar el archivo .env
load_dotenv()

def procesar_anuncio(request, numero_url):
    # Obtener el anuncio desde la base de datos
    anuncio = get_object_or_404(AnuncioBoib, numero_url=numero_url)
    
    if not anuncio.texto_completo:
        return JsonResponse({"error": "El anuncio no tiene texto_completo"}, status=400)
    
    #Juntamos el texto del resumen con el texto completo del anuncio
    texto_proceso = "fecha de publicación BOIB: " + str(anuncio.fecha) + anuncio.texto_resolucion + anuncio.texto_completo
    
    # Configurar API Key y Assistant ID
    API_KEY = os.environ.get('OPENAI_API_KEY')
    ASSISTANT_ID = os.environ.get('ASSISTANT_ID')
    
    # Crear el cliente OpenAI
    client = OpenAI(api_key=API_KEY)
    
    # Crear un hilo de conversación
    thread = client.beta.threads.create(extra_headers={"OpenAI-Beta": "assistants=v2"})
    
    # Agregar mensaje al hilo
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=texto_proceso,
        extra_headers={"OpenAI-Beta": "assistants=v2"}
    )
    
    # Ejecutar el asistente
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        extra_headers={"OpenAI-Beta": "assistants=v2"}
    )
    
    # Esperar la respuesta del asistente
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
            extra_headers={"OpenAI-Beta": "assistants=v2"}
        )
        
        if run_status.status in ["completed", "failed", "cancelled"]:
            break
        time.sleep(2)
    
    # Obtener la respuesta del asistente y guardar en la base de datos
    if run_status.status == "completed":
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            extra_headers={"OpenAI-Beta": "assistants=v2"}
        )
        
        for msg in messages.data[::-1]:  # Recorrer mensajes en orden inverso
            if msg.role == "assistant":
                json_response = json.loads(msg.content[0].text.value)  # Extraer solo el contenido JSON
                print(json_response)
                # Guardar en la base de datos
                anuncio_procesado, created = AnuncioBoibProcesado.objects.update_or_create(
                    anuncio=anuncio,
                    defaults={
                        "link_html": anuncio.link_html,
                        "entidad_convocante": anuncio.entidad,
                        "isla": json_response["isla"],
                        "numero_anuncio": json_response["numero_anuncio"],
                        "cuerpo_trabajo": json_response["cuerpo_trabajo"],
                        "numero_plazas": json_response["numero_plazas"],
                        "grupo_profesional": json_response["grupo_profesional"],
                        "tipo_proceso": json_response["tipo_proceso"],
                        "tipo_turno": json_response["tipo_turno"],
                        "tipo_personal": json_response["tipo_personal"],
                        "fase_proceso": json_response["fase_proceso"],
                        "requisitos": json_response["requisitos"],
                        "plazo_presentacion": json_response["plazo_presentacion"],
                        "fecha_publicacion": anuncio.fecha,
                        "fecha_maxima_presentacion": json_response["fecha_maxima_presentacion"] if json_response["fecha_maxima_presentacion"] else None
                    }
                )
                #print(anuncio.link_html, json_response["plazo_presentacion"], anuncio.fecha, json_response["fecha_maxima_presentacion"])
                return JsonResponse({"message": "Procesamiento exitoso", "created": created})
    else:
        return JsonResponse({"error": f"La ejecución falló con estado: {run_status.status}"}, status=500)
    
def procesar_anuncios_pendientes(request):
    # Obtener todos los numero_url de AnuncioBoib
    anuncios_existentes = set(AnuncioBoib.objects.values_list("numero_url", flat=True))
    
    # Obtener todos los numero_url de AnuncioBoibProcesado
    anuncios_procesados = set(AnuncioBoibProcesado.objects.values_list("anuncio", flat=True))
    
    # Encontrar los anuncios que aún no han sido procesados
    anuncios_pendientes = anuncios_existentes - anuncios_procesados
    
    if not anuncios_pendientes:
        print("No hay anuncios pendientes por procesar")
        return JsonResponse({"message": "No hay anuncios pendientes por procesar"})
    
    resultados = []
    for numero_url in anuncios_pendientes:
        respuesta = procesar_anuncio(request, numero_url)
        try:
            resultados.append(json.loads(respuesta.content))
        except json.JSONDecodeError:
            resultados.append({"error": f"Fallo al procesar anuncio {numero_url}"})
    
    return JsonResponse({"resultados": resultados})
    
def anuncios_IA_recientes(request):
    """Renderiza la base de datos de ofertas IA 'procesador_IA/anuncios.html'
    """

    # Filtrar los anuncios  y ordenarlos por fecha descendente
    anuncios = AnuncioBoibProcesado.objects.all().order_by('-fecha_publicacion')
    return render(request, 'procesador_IA/anuncios.html', {'anuncios': anuncios})