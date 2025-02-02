# examinador/management/commands/generate_csv.py
# Se usa: python manage.py generate_csv --input_folder="preguntas_txt" --output_file="db.csv"

import csv
import os
import re

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Procesa archivos .txt en el directorio preguntas_txt y genera un archivo preguntas_procesadas.csv'

    def handle(self, *args, **kwargs):
        directorio_actual = os.path.join(os.getcwd(), 'preguntas_txt')
        if not os.path.exists(directorio_actual):
            self.stdout.write(self.style.ERROR(f"El directorio {directorio_actual} no existe."))
            return
        
        self.stdout.write(f"Directorio actual: {directorio_actual}")

        archivos_txt = [archivo for archivo in os.listdir(directorio_actual) if archivo.endswith('.txt')]
        if not archivos_txt:
            self.stdout.write(self.style.WARNING("No se encontraron archivos .txt en el directorio preguntas_txt."))
            return
        
        datos_totales = []
        for archivo_txt in archivos_txt:
            self.stdout.write(f"Procesando archivo: {archivo_txt}")
            ruta_archivo = os.path.join(directorio_actual, archivo_txt)
            datos_procesados = self.procesar_archivo_txt(ruta_archivo)
            datos_totales.extend(datos_procesados)
        
        archivo_csv = os.path.join(directorio_actual, 'preguntas_test.csv')
        self.guardar_datos_en_csv(datos_totales, archivo_csv)

        self.stdout.write(self.style.SUCCESS(f"Se han procesado {len(archivos_txt)} archivos .txt y los datos se han guardado en {archivo_csv}."))

    def transformar_correcta(self, valor):
        """Transforma la letra de la respuesta correcta en un valor numérico."""
        mapeo = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        return mapeo.get(valor.lower(), 0)

    def procesar_archivo_txt(self, archivo_txt):
        """Procesa un archivo .txt y devuelve una lista de datos procesados."""
        datos_procesados = []
        nombre_normativa = os.path.splitext(os.path.basename(archivo_txt))[0]

        with open(archivo_txt, 'r', encoding='utf-8') as file:
            lineas = file.readlines()

        for i, linea in enumerate(lineas, start=1):
            try:
                partes = re.split(r'"\s*,\s*"', linea.strip())
                
                if len(partes) == 7:
                    pregunta, respuesta_a, respuesta_b, respuesta_c, respuesta_d, correcta, justificacion = partes

                    pregunta = pregunta.strip('"')
                    respuesta_a = respuesta_a.strip('"')
                    respuesta_b = respuesta_b.strip('"')
                    respuesta_c = respuesta_c.strip('"')
                    respuesta_d = respuesta_d.strip('"')
                    justificacion = justificacion.strip('"')

                    correcta_numerica = self.transformar_correcta(correcta)

                    datos_procesados.append([
                        pregunta, respuesta_a, respuesta_b, respuesta_c,
                        respuesta_d, correcta_numerica, justificacion, nombre_normativa
                    ])
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Formato incorrecto en la línea {i} del archivo {archivo_txt}: {linea.strip()} (Campos detectados: {len(partes)})"
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Error al procesar la línea {i} del archivo {archivo_txt}: {linea.strip()}\nDetalles del error: {e}"
                ))

        return datos_procesados

    def guardar_datos_en_csv(self, datos_totales, archivo_csv):
        """Guarda todos los datos procesados en un archivo .csv sin encabezado."""
        with open(archivo_csv, 'w', newline='', encoding='utf-8') as file:
            escritor_csv = csv.writer(file)
            escritor_csv.writerows(datos_totales)