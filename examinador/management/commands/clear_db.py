# examinador/management/commands/clear_db.py
# Se usa el comando 'python manage.py clear_db'

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Opositorium.settings')  # Reemplaza 'tu_proyecto' con el nombre de tu proyecto
#django.setup()

from django.core.management.base import BaseCommand
from django.db import connection  # Para ejecutar consultas SQL directas
from examinador.models import Pregunta

class Command(BaseCommand):
    help = "Vacía la base de datos de preguntas y reinicia el contador de ID. Se usa el comando 'python manage.py clear_db'"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('¿Estás seguro de que quieres vaciar la base de datos? (s/n)'))
        confirmacion = input()

        if confirmacion.lower() == 's':
            # Eliminar todos los registros
            Pregunta.objects.all().delete()

            # Reiniciar el contador de ID para la tabla
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='preguntas_test';")

            self.stdout.write(self.style.SUCCESS('Base de datos vaciada exitosamente y contador de ID reiniciado.'))
        else:
            self.stdout.write(self.style.INFO('Operación cancelada.'))