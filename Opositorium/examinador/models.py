# examinador/models.py

from django.db import models

class Pregunta(models.Model):
    pregunta = models.CharField(max_length=512)
    respuesta1 = models.CharField(max_length=512)
    respuesta2 = models.CharField(max_length=512)
    respuesta3 = models.CharField(max_length=512)
    respuesta4 = models.CharField(max_length=512)
    correcta = models.IntegerField()  # 1, 2, 3, o 4
    justificacion = models.CharField(max_length=512)
    normativa = models.CharField(max_length=512)

    def __str__(self):
        return self.pregunta
