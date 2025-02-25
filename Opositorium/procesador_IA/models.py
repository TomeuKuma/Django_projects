from django.db import models
from boib_scraper.models import AnuncioBoib

class AnuncioBoibProcesado(models.Model):
    anuncio = models.OneToOneField(
        AnuncioBoib,
        on_delete=models.PROTECT,  # Evita que el anuncio referenciado sea eliminado
        to_field='numero_url',
        primary_key=True,  # Sigue siendo la clave primaria
    )
    link_html = models.URLField(blank=True, null=True)
    entidad_convocante = models.CharField(max_length=255)
    isla = models.CharField(max_length=50)
    numero_anuncio = models.CharField(max_length=50, blank=True, null=True)
    cuerpo_trabajo = models.JSONField(blank=True, null=True)
    numero_plazas = models.JSONField(blank=True, null=True)
    grupo_profesional = models.JSONField(blank=True, null=True)
    tipo_proceso = models.CharField(max_length=50, blank=True, null=True)
    tipo_turno = models.CharField(max_length=50, blank=True, null=True)
    tipo_personal = models.CharField(max_length=50, blank=True, null=True)
    fase_proceso = models.CharField(max_length=50, blank=True, null=True)
    requisitos = models.JSONField(blank=True, null=True)
    plazo_presentacion = models.JSONField(blank=True, null=True)
    fecha_publicacion = models.DateField(blank=True, null=True)
    fecha_maxima_presentacion = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'anuncios_boib_IA'
