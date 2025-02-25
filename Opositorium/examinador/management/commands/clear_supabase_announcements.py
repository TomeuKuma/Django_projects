# examinador/management/commands/clear_supabase.py 
# Se usa el comando 'python manage.py clear_supabase_announcements'

from django.core.management.base import BaseCommand
from django.db import connection  # Para ejecutar consultas SQL directas
from boib_scraper.models import AnuncioBoib

class Command(BaseCommand):
    help = "Vacía la base de datos de preguntas y reinicia el contador de ID en PostgreSQL. Se usa el comando 'python manage.py clear_supabase_announcements'"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('¿Estás seguro de que quieres vaciar la base de datos? (s/n)'))
        confirmacion = input()

        if confirmacion.lower() == 's':
            # Eliminar todos los registros de la tabla
            AnuncioBoib.objects.all().delete()

            # Reiniciar el contador de ID en PostgreSQL
            #with connection.cursor() as cursor:
            #    cursor.execute("ALTER SEQUENCE examinador_pregunta_id_seq RESTART WITH 1;")

            self.stdout.write(self.style.SUCCESS('Base de datos vaciada exitosamente y contador de ID reiniciado.'))
        else:
            self.stdout.write(self.style.INFO('Operación cancelada.'))
