# examinador/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.configuracion, name='configuracion'),
    path('iniciar/', views.iniciar_examen, name='iniciar_examen'),
    path('pregunta/', views.pregunta, name='pregunta'),
    path('comprobar/', views.comprobar_respuesta, name='comprobar_respuesta'),
    path('resultados/', views.resultados, name='resultados'),
    path('siguiente/', views.siguiente_pregunta, name='siguiente_pregunta'),
    path('anterior/', views.anterior_pregunta, name='anterior_pregunta'),
]
