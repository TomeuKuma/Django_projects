# boib_scraper/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('anuncios', views.anuncios_recientes, name='anuncios'),
]