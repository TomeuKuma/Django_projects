# boib_scraper/models.py

from django.db import models

class AnuncioBoib(models.Model):
    url_id = models.IntegerField()
    fecha = models.DateField()
    boletin = models.CharField(max_length=20)
    numero_boletin = models.IntegerField()
    administracion = models.CharField(max_length=128)
    entidad = models.CharField(max_length=128)
    texto_resolucion = models.TextField(null=True, blank=True)
    link_pdf = models.URLField(max_length=256)
    link_html = models.URLField(max_length=256)
    link_xml = models.URLField(max_length=256)
    texto_completo = models.TextField(null=True, blank=True)
    numero_registro = models.IntegerField()
    numero_url = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.url_id)

    class Meta:
        db_table = 'anuncios_boib'
