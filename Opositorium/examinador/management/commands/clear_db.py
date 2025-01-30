# examinador/management/commands/clear_db.py
# Se usa el comando 'python manage.py clear_db'

#import os
#import django

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Opositorium.settings')  # Reemplaza 'tu_proyecto' con el nombre de tu proyecto
#django.setup()

from django.core.management.base import BaseCommand
from examinador.models import Pregunta  # Importa tu modelo Pregunta

class Command(BaseCommand):
    help = "Vacía la base de datos de preguntas. Se usa el comando 'python manage.py clear_db'"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('¿Estás seguro de que quieres vaciar la base de datos? (s/n)'))
        confirmacion = input()

        if confirmacion.lower() == 's':
            Pregunta.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Base de datos vaciada exitosamente'))
        else:
            self.stdout.write(self.style.INFO('Operación cancelada'))