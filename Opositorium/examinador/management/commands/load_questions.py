# examinador/management/commands/load_questions.py
# Se usa el comando python manage.py load_questions nombre_csv

import csv
from django.core.management.base import BaseCommand
from examinador.models import Pregunta

class Command(BaseCommand):
    help = "Carga preguntas desde un archivo CSV. Se usa el comando 'python manage.py load_questions nombre_csv'"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                Pregunta.objects.create(
                    pregunta=row[0],
                    respuesta1=row[1],
                    respuesta2=row[2],
                    respuesta3=row[3],
                    respuesta4=row[4],
                    correcta=int(row[5]),
                    justificacion=row[6],
                    normativa=row[7]
                )
        self.stdout.write(self.style.SUCCESS('Preguntas cargadas exitosamente'))