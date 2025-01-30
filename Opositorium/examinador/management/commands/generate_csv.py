# examinador/management/commands/generate_csv.py
# Se usa: python manage.py generate_csv --input_folder="preguntas_txt" --output_file="db.csv"

import os
import csv
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Genera un archivo CSV consolidado a partir de los archivos .txt de la carpeta 'preguntas_txt'"

    def add_arguments(self, parser):
        parser.add_argument(
            '--input_folder',
            type=str,
            default='preguntas_txt',
            help='Carpeta donde se encuentran los archivos .txt',
        )
        parser.add_argument(
            '--output_file',
            type=str,
            default='preguntas_consolidadas.csv',
            help='Nombre del archivo CSV de salida',
        )

    def handle(self, *args, **kwargs):
        input_folder = kwargs['input_folder']
        output_file = kwargs['output_file']

        # Validar que la carpeta de entrada existe
        if not os.path.exists(input_folder):
            self.stderr.write(f"Error: La carpeta '{input_folder}' no existe.")
            return

        # Crear el archivo CSV de salida
        with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)  # Comillas para strings

            # Procesar cada archivo .txt en la carpeta
            for filename in os.listdir(input_folder):
                if filename.endswith('.txt'):
                    file_path = os.path.join(input_folder, filename)
                    archivo_origen = os.path.splitext(filename)[0]  # Nombre del archivo sin extensión

                    # Leer el archivo .txt línea por línea
                    with open(file_path, mode='r', encoding='utf-8') as txtfile:
                        for line in txtfile:
                            line = line.strip()  # Eliminar espacios y saltos de línea
                            if not line:
                                continue  # Ignorar líneas vacías

                            # Separar los datos por comas
                            datos = line.split('","')
                            datos = [d.strip('"') for d in datos]  # Quitar las comillas iniciales y finales

                            if len(datos) != 7:
                                self.stderr.write(f"Advertencia: Línea inválida en '{filename}': {line}")
                                continue

                            # Transformar el campo "correcta"
                            correcta_map = {"a": 1, "b": 2, "c": 3, "d": 4}
                            correcta_transformada = correcta_map.get(datos[5].lower(), datos[5])

                            # Añadir el archivo origen al registro
                            registro_csv = datos[:5] + [correcta_transformada, datos[6], archivo_origen]

                            # Escribir el registro en el CSV
                            csv_writer.writerow(registro_csv)

        self.stdout.write(self.style.SUCCESS(f"Archivo CSV consolidado generado exitosamente: {output_file}"))