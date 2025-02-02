# examinador/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Pregunta(models.Model):
    pregunta = models.CharField(max_length=512)
    respuesta1 = models.CharField(max_length=512)
    respuesta2 = models.CharField(max_length=512)
    respuesta3 = models.CharField(max_length=512)
    respuesta4 = models.CharField(max_length=512)
    correcta = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])  # 1, 2, 3, o 4
    justificacion = models.CharField(max_length=512)
    normativa = models.CharField(max_length=512)

    def __str__(self):
        return self.pregunta

    class Meta:
        db_table = 'preguntas_test'