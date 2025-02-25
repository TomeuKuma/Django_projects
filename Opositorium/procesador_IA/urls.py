from django.urls import path
from . import views

urlpatterns = [
    path('', views.anuncios_IA_recientes, name='anuncios_IA_recientes'),
    path('procesar_anuncio/<int:numero_url>/', views.procesar_anuncio, name='procesar_anuncio'),
    path('procesar_pendientes/', views.procesar_anuncios_pendientes, name='procesar_pendientes'),
]