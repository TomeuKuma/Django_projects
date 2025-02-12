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
from django.contrib.auth.decorators import login_required

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

@login_required
def configuracion(request):
    # Obtener todas las normativas únicas de la base de datos
    normativas = Pregunta.objects.values_list('normativa', flat=True).distinct()
    return render(request, 'examinador/configuracion.html', {'normativas': normativas})

# Inicia el examen según el número de preguntas seleccionadas
@login_required
def iniciar_examen(request):
    if request.method == 'POST':
        num_preguntas = int(request.POST.get('num_preguntas', 10))
        tasa_descuento = float(request.POST.get('tasa_descuento', 0))
        normativas_seleccionadas = request.POST.getlist('normativas')
        
        if not normativas_seleccionadas:
            messages.error(request, "*Debes seleccionar al menos una normativa.")
            return redirect('configuracion')

        preguntas_filtradas = Pregunta.objects.filter(normativa__in=normativas_seleccionadas)
        num_preguntas = min(num_preguntas, preguntas_filtradas.count())
        preguntas_seleccionadas = random.sample(list(preguntas_filtradas), num_preguntas)
        
        request.session['preguntas_ids'] = [pregunta.id for pregunta in preguntas_seleccionadas]
        request.session['respuestas'] = {}
        request.session['pregunta_actual'] = 0
        request.session['correctas'] = 0
        request.session['incorrectas'] = 0
        request.session['no_contestadas'] = 0
        request.session['hora_inicio'] = datetime.now().isoformat()
        request.session['tasa_descuento'] = tasa_descuento
        
        return redirect('pregunta')
    else:
        return redirect('configuracion')

# Muestra la pregunta actual
@login_required
def pregunta(request):
    pregunta_actual = request.session.get('pregunta_actual', 0)
    preguntas_ids = request.session.get('preguntas_ids', [])
    
    if pregunta_actual >= len(preguntas_ids):
        return redirect('resultados')

    pregunta = Pregunta.objects.get(id=preguntas_ids[pregunta_actual])
    return render(request, 'examinador/pregunta.html', {'pregunta': pregunta})

# Comprueba la respuesta del usuario
@login_required
def comprobar_respuesta(request):
    if request.method == 'POST':
        pregunta_id = request.POST.get('pregunta_id')
        respuesta = request.POST.get('respuesta')
        
        respuestas = request.session.get('respuestas', {})
        
        if respuesta:
            respuesta = int(respuesta)
            pregunta = Pregunta.objects.get(id=pregunta_id)
            es_correcta = pregunta.correcta == respuesta
            respuestas[pregunta_id] = es_correcta
            if es_correcta:
                request.session['correctas'] += 1
            else:
                request.session['incorrectas'] += 1
        else:
            respuestas[pregunta_id] = None  # No contestada
            request.session['no_contestadas'] += 1

        request.session['respuestas'] = respuestas

        # Retorna feedback al usuario
        return JsonResponse({
            'es_correcta': es_correcta if respuesta else False,
            'justificacion': pregunta.justificacion if respuesta else Pregunta.objects.get(id=pregunta_id).justificacion
        })

# Avanza a la siguiente pregunta
@login_required
def siguiente_pregunta(request):
    request.session['pregunta_actual'] += 1
    return redirect('pregunta')

# Retrocede a la pregunta anterior
@login_required
def anterior_pregunta(request):
    request.session['pregunta_actual'] -= 1
    return redirect('pregunta')

# Muestra los resultados del examen
@login_required
def resultados(request):
    correctas = request.session.get('correctas', 0)
    incorrectas = request.session.get('incorrectas', 0)
    no_contestadas = request.session.get('no_contestadas', 0)
    total = correctas + incorrectas + no_contestadas
    tasa_descuento = request.session.get('tasa_descuento', 0)
    try:
        nota = round(((correctas - (incorrectas * tasa_descuento)) / total) * 10, 2)
    except ZeroDivisionError:
        nota = 0

    
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
        'incorrectas': incorrectas,
        'no_contestadas': no_contestadas,
        'total': total,
        'nota': nota,
        'tiempo_total': tiempo_total
    })
