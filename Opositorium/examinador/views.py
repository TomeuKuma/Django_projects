# examinador/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import F
from .models import Pregunta
from datetime import datetime
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
import random

def index(request):
    return render(request, 'examinador/index.html')

def contacto(request):
    return render(request, 'examinador/contacto.html')

def contacto_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('name')
        email = request.POST.get('email')
        mensaje = request.POST.get('message')

        # Enviar el correo
        send_mail(
            f'Nuevo mensaje de {nombre}',
            mensaje,
            email,
            ['bartomeumirallesllull@gmail.com'],
            fail_silently=False,
        )

        return HttpResponseRedirect('/contacto/')  # Redirige tras enviar

    return render(request, 'examinador/contacto.html')

def configuracion(request):
    # Obtener todas las normativas únicas de la base de datos
    normativas = Pregunta.objects.values_list('normativa', flat=True).distinct()
    return render(request, 'examinador/configuracion.html', {'normativas': normativas})

# Inicia el examen según el número de preguntas seleccionadas
def iniciar_examen(request):
    if request.method == 'POST':
        num_preguntas = int(request.POST.get('num_preguntas', 10))
        normativas_seleccionadas = request.POST.getlist('normativas')  # Obtén todas las normativas seleccionadas

        # Filtrar preguntas según las normativas seleccionadas
        if normativas_seleccionadas:
            preguntas_filtradas = Pregunta.objects.filter(normativa__in=normativas_seleccionadas)
        else:
            #preguntas_filtradas = Pregunta.objects.all()  # En caso de no seleccionar ninguna, tomar todas
            messages.error(request, "*Debes seleccionar al menos una normativa.")
            return redirect('configuracion')

        total_preguntas_disponibles = preguntas_filtradas.count()

        # Limitar al número máximo de preguntas disponibles
        num_preguntas = min(num_preguntas, total_preguntas_disponibles)

        # Seleccionar preguntas aleatorias
        preguntas_seleccionadas = random.sample(list(preguntas_filtradas), num_preguntas)

        # Guardar las preguntas seleccionadas en la sesión
        request.session['preguntas_ids'] = [pregunta.id for pregunta in preguntas_seleccionadas]
        request.session['respuestas'] = {}
        request.session['pregunta_actual'] = 0
        request.session['hora_inicio'] = datetime.now().isoformat()
        return redirect('pregunta')
    else:
        return redirect('configuracion')

# Muestra la pregunta actual
def pregunta(request):
    pregunta_actual = request.session.get('pregunta_actual', 0)
    preguntas_ids = request.session.get('preguntas_ids', [])
    
    if pregunta_actual >= len(preguntas_ids):
        return redirect('resultados')

    pregunta_id = preguntas_ids[pregunta_actual]
    pregunta = Pregunta.objects.get(id=pregunta_id)
    return render(request, 'examinador/pregunta.html', {'pregunta': pregunta})

# Comprueba la respuesta del usuario
def comprobar_respuesta(request):
    if request.method == 'POST':
        pregunta_id = request.POST.get('pregunta_id')
        respuesta = int(request.POST.get('respuesta'))
        pregunta = Pregunta.objects.get(id=pregunta_id)
        es_correcta = pregunta.correcta == respuesta

        # Guarda la respuesta en la sesión
        respuestas = request.session.get('respuestas', {})
        respuestas[pregunta_id] = es_correcta  # True si es correcta, False si es incorrecta
        request.session['respuestas'] = respuestas

        # Retorna feedback al usuario
        return JsonResponse({
            'es_correcta': es_correcta,
            'justificacion': pregunta.justificacion
        })

# Avanza a la siguiente pregunta
def siguiente_pregunta(request):
    request.session['pregunta_actual'] += 1
    return redirect('pregunta')

# Retrocede a la pregunta anterior
def anterior_pregunta(request):
    request.session['pregunta_actual'] -= 1
    return redirect('pregunta')

# Muestra los resultados del examen
def resultados(request):
    respuestas = request.session.get('respuestas', {})
    correctas = sum(1 for correcta in respuestas.values() if correcta)
    total = len(respuestas)
    aciertos = round(correctas / total * 100, 2) if total > 0 else 0
    resultado = "aprobado" if aciertos >= 50 else "suspendido"
        
    # Calcular el tiempo transcurrido
    hora_inicio = request.session.get('hora_inicio')
    if hora_inicio:
        hora_inicio = datetime.fromisoformat(hora_inicio)
        tiempo_transcurrido = datetime.now() - hora_inicio
        horas, resto = divmod(tiempo_transcurrido.total_seconds(), 3600)
        minutos, segundos = divmod(resto, 60)
        tiempo_total = f"{int(horas)} horas, {int(minutos)} minutos, {int(segundos)} segundos"
    else:
        tiempo_total = None
        
    return render(request, 'examinador/resultados.html', {
        'correctas': correctas,
        'total': total,
        'aciertos': aciertos,
        'resultado': resultado,
        'tiempo_total': tiempo_total
    })
