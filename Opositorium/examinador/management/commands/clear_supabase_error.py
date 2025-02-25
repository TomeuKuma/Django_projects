# examinador/management/commands/clear_supabase_error.py 
# Se usa el comando 'python manage.py clear_supabase_error'

from django.core.management.base import BaseCommand
from django.db import connection  # Para ejecutar consultas SQL directas
from examinador.models import ErrorReport

class Command(BaseCommand):
    help = "Vacía la base de datos de reportes de errores y reinicia el contador de ID en PostgreSQL. Se usa el comando 'python manage.py clear_supabase_error'"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('¿Estás seguro de que quieres vaciar la base de datos de reportes de errores? (s/n)'))
        confirmacion = input()

        if confirmacion.lower() == 's':
            # Eliminar todos los registros de la tabla
            ErrorReport.objects.all().delete()

            # Reiniciar el contador de ID en PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute("ALTER SEQUENCE examinador_errorreport_id_seq RESTART WITH 1;")

            self.stdout.write(self.style.SUCCESS('Base de datos de reportes de errores vaciada exitosamente y contador de ID reiniciado.'))
        else:
            self.stdout.write(self.style.INFO('Operación cancelada.'))
