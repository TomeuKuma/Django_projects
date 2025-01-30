# examinador/management/commands/generate_csv.py

import os
import csv
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Junta los archivos .txt individuales y convierte el resultado a formato .csv'

    def add_arguments(self, parser):
        parser.add_argument('directorio_txt', type=str, help='Directorio que contiene los archivos .txt')

    def handle(self, *args, **options):
        directorio_txt = options['directorio_txt']
        archivos_txt = [f for f in os.listdir(directorio_txt) if f.endswith('.txt')]

        if not archivos_txt:
            self.stdout.write(self.style.WARNING('No se encontraron archivos .txt en el directorio especificado.'))
            return

        nombre_archivo_csv = 'db.csv'
        ruta_archivo_csv = os.path.join(directorio_txt, nombre_archivo_csv)

        try:
            with open(ruta_archivo_csv, 'w', newline='', encoding='utf-8') as archivo_csv:
                writer = csv.writer(archivo_csv, quoting=csv.QUOTE_ALL)

                # Escribir datos sin encabezado
                for archivo_txt in archivos_txt:
                    ruta_completa_txt = os.path.join(directorio_txt, archivo_txt)
                    try:
                        with open(ruta_completa_txt, 'r', encoding='utf-8') as archivo_txt_actual:
                            for linea in archivo_txt_actual:
                                datos = linea.strip().split(',')

                                # Manejar líneas incompletas
                                if len(datos) < 8:
                                    self.stdout.write(self.style.WARNING(f'Línea incompleta en {archivo_txt}: {linea.strip()}'))
                                    continue

                                # Limpiar datos
                                datos = [dato.strip() if dato else None for dato in datos]

                                # Convertir 'correcta' a número *y actualizar la variable correcta*
                                respuesta_correcta = datos[5].lower()
                                correcta_num = None  # Inicializar a None
                                if respuesta_correcta == 'a':
                                    correcta_num = int(1)
                                elif respuesta_correcta == 'b':
                                    correcta_num = int(2)
                                elif respuesta_correcta == 'c':
                                    correcta_num = int(3)
                                elif respuesta_correcta == 'd':
                                    correcta_num = int(4)
                                else:
                                    self.stdout.write(self.style.WARNING(f'Respuesta incorrecta en {archivo_txt}: {linea.strip()}'))

                                datos[5] = correcta_num  # Asignar el valor numérico a la lista *antes* de escribir

                                datos[7] = archivo_txt[:-4]  # Asignar normativa (sin extensión)
                                writer.writerow(datos) # Escribir la *lista actualizada*

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error al leer el archivo {archivo_txt}: {e}'))
                        return

            self.stdout.write(self.style.SUCCESS(f'Archivo CSV "{nombre_archivo_csv}" creado exitosamente en "{directorio_txt}".'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al crear el archivo CSV: {e}'))
            return