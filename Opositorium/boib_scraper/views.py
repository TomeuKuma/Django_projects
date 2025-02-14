# boib_scraper/views.py

import requests
import datetime
import warnings
import pandas as pd
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
from django.db import models
from django.shortcuts import render
from django.utils.timezone import now, timedelta
from .models import AnuncioBoib

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def current_bulletin_id():
  """Escrapea los datos en el apartado de última publicación de boletín
  y devuelve la 'url_id del último ejemplar publicado"""
  last_bulletin_url = 'http://www.caib.es/eboibfront/'
  page = requests.get(last_bulletin_url)
  soup = BeautifulSoup(page.content, 'lxml')
  # Devuelve el nº de url del ultimo boletin disponible
  links = soup.find_all("a", href=lambda href: href and "/eboibfront/ca/" in href)
  link_list = [link["href"].split('/')[-2] for link in links]
  return link_list[0]

class BulletinScraper:
    """Clase con los atributos y funciones comunes para
    realizar scraping sobre cualquier Boletín Oficial"""

    def __init__(self, url_id):
        self.url_id = int(url_id)
        self.date_list = []
        self.bulletin_list = []
        self.number_list = []
        self.authority_list = []
        self.entity_list = []
        self.resolution_list = []
        self.register_list = []
        self.pdf_link_list = []
        self.html_link_list = []
        self.xml_link_list = []
        self.url_number_list = []
        self.data = pd.DataFrame()
        self.json_list = []

    def clear_lists(self):
        """Vacía los atributos de la clase BulletinScraper"""
        self.date_list = []
        self.bulletin_list = []
        self.number_list = []
        self.authority_list = []
        self.entity_list = []
        self.resolution_list = []
        self.register_list = []
        self.pdf_link_list = []
        self.html_link_list = []
        self.xml_link_list = []
        self.url_number_list = []
        self.data = pd.DataFrame()
        self.json_list = []

    def make_dataframe(self):
        """Crea un dataframe con cabeceras desde los datos guardados
        en las listas de la clase BulletinScraper"""
        list_merge = {'URL_id': self.url_id,
                      'Fecha': self.date_list,
                      'Boletín': self.bulletin_list,
                      'Número': self.number_list,
                      'Administración': self.authority_list,
                      'Entidad': self.entity_list,
                      'Resolución': self.resolution_list,
                      'PDF': self.pdf_link_list,
                      'HTML': self.html_link_list,
                      'XML': self.xml_link_list,
                      'Nº Registro': self.register_list,
                      'Nº URL': self.url_number_list}
        self.data = pd.DataFrame(data=list_merge)
        #pd.set_option('display.max_columns', None)
        return self.data

    def make_json(self):
        """Crea un json con cabeceras desde los datos guardados
        en las listas de la clase BulletinScraper"""

        for element in range(len(self.date_list)):
            merged_ele = {'URL_id': self.url_id,
                          'Fecha': self.date_list[element].isoformat(),
                          'Boletin': self.bulletin_list[element],
                          'Numero': self.number_list[element],
                          'Administracion': self.authority_list[element],
                          'Entidad': self.entity_list[element],
                          'Resolucion': self.resolution_list[element],
                          'PDF': self.pdf_link_list[element],
                          'HTML': self.html_link_list[element],
                          'XML': self.xml_link_list[element],
                          'N_Registro': self.register_list[element],
                          'N_URL': self.url_number_list[element]}
            self.json_list.append(merged_ele)


class BoibScraper(BulletinScraper):
    """ Clase con los atributos y funciones específicas para
    realizar scraping sobre el Boletin Oficial de les Illes Balears.
    Se le debe pasar el parámetro 'url_id' con formato 'numero'"""
    def __init__(self, url_id='10140'): #el mas antiguo es '10140'
        super().__init__(url_id)
        self.url = 'https://www.caib.es/eboibfront/es/2020/' + str(url_id) + '/seccio-ii-autoritats-i-personal/473'
        self.current_bulletin_id = self.current_bulletin_id()

    def announcement_scraping_loop(self, block_2_2):
        """ Rasca los datos de la web y los guarda en los atributos de la clase BulletinScraper
        :param block_2_2: Ubicación html de la sección de anuncios de oposiciones y concursos
        :return: None
        """
        announcements = block_2_2.find_all('div', {'class': 'caja'})
        for announcement in announcements:
            links_bs4 = announcement.findAll('a', href=True)
            for link in links_bs4:

                if link['class'] == ['pdf']:
                    full_link = "https://www.caib.es" + link['href']
                    self.pdf_link_list.append(full_link)

                elif link['class'] == ['html']:
                    full_link = link['href']
                    self.html_link_list.append(full_link)

                elif link['class'] == ['rdf']:
                    full_link = link['href']
                    page = requests.get(full_link)
                    soup = BeautifulSoup(page.content, 'lxml')

                    # Link XML
                    self.xml_link_list.append(full_link)
                    # Fecha
                    publication_date = str(soup.find_all('dc:date')[0]).replace('<dc:date>', '').replace('</dc:date>',
                                                                                                         '')
                    publication_date = datetime.datetime.strptime(publication_date, '%Y-%m-%d').date()
                    self.date_list.append(publication_date)
                    # NºRegistro
                    self.register_list.append(
                        str(soup.find_all('env:numeroregistre')).replace('[<env:numeroregistre>', '').replace(
                            '</env:numeroregistre>]', ''))
                    # NºURL
                    self.url_number_list.append(str(full_link).split('/')[-3])
                    # print(str(full_link).split('/')[-3])

                else:
                    print('Error en el scraping de links')
                    break

            # Nombre de boletín
            self.bulletin_list.append("BOIB")
            # Número del boletín
            page = requests.get(self.url)
            soup = BeautifulSoup(page.content, 'lxml')
            num = soup.find_all('strong')
            number = int(num[1].get_text().replace('Núm.', ''))
            self.number_list.append(str(number))
            # Nombre de entidad
            entity_bs4 = BeautifulSoup(announcement.find('h3', {'class': 'organisme'}).find('strong').text, 'lxml')
            entity_text = entity_bs4.get_text()
            self.entity_list.append(entity_text)
            # Nombre de la Administración
            authority_bs4 = BeautifulSoup(announcement.find('h3', {'class': 'organisme'}).text, 'lxml')
            authority_text = authority_bs4.get_text().strip('\n')
            if authority_text != entity_text:
                authority_text = authority_text.replace(entity_text, '')
            self.authority_list.append(authority_text)
            # Resolución completa
            resolution_bs4 = BeautifulSoup(announcement.find('ul', {'class': 'resolucions'}).text, 'lxml')
            resolution_text = resolution_bs4.get_text().replace('\r', ' ').replace('\n', '')
            resolution_text = resolution_text.replace('\t', '').split('Número')
            self.resolution_list.append(resolution_text[0])

    def get_data(self):
        """ Comprueba que existan los apartados del BOIB y ejecuta el loop sobre los anuncios.
        Guarda el número de BOIB con errores, si los hay"""
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'lxml')
        block_2 = soup.find_all('ul', {'class': 'entitats'})
        tester = soup.find_all('ul', {'class': 'llistat'})
        
        # Comprobamos que existe la sección primera del apartado de nombramientos y autoridades:
        try:
            # Si existe la sección primera, instanciamos la sección segunda
            if str(tester[0]).find('Subsección primera.') >= 0:
                block_2_2 = block_2[1]
                # Recorremos los anuncios de la sección segunda
                self.announcement_scraping_loop(block_2_2)

            # Si no existe la sección primera:
            else:
                # Si existe la sección segunda, la instanciamos:
                if str(tester[0]).find('Subsección segunda.') >= 0:
                    block_2_2 = block_2[0]
                    # Recorremos los anuncios de la sección segunda
                    self.announcement_scraping_loop(block_2_2)

                # Si no existe la sección primera ni segunda:
                else:
                    print('No hay oposiciones/convocatorias en el BOIB con URL: ', self.url)
            df = self.make_dataframe()
            #self.make_dataframe()
            self.make_json()
            return df 
        except:
            print('No existe el BOIB con URL: ', self.url)

    def current_bulletin_id(self):
        """Escrapea los datos en el apartado de última publicación de boletín
        y devuelve la 'url_id del último ejemplar publicado"""
        last_bulletin_url = 'http://www.caib.es/eboibfront/'
        page = requests.get(last_bulletin_url)
        soup = BeautifulSoup(page.content, 'lxml')
        # Devuelve el nº de url del ultimo boletin disponible
        links = soup.find_all("a", href=lambda href: href and "/eboibfront/ca/" in href)
        link_list = [link["href"].split('/')[-2] for link in links]
        return link_list[0]
    
    def scrape_boib(self):
        print(f'🔎 Intentando rascar datos de {self.url_id}')
        # Aquí pones la lógica de scraping
        print(f'🔍 Datos obtenidos: {self.url}')
    
def dataframe_to_db(df):
    """
    Guarda un DataFrame en la base de datos sin duplicar registros existentes.
    Usa 'numero_url' como identificador único.
    """
    # Obtener los valores únicos de 'numero_url' ya almacenados en la BD
    urls_existentes = set(AnuncioBoib.objects.values_list("numero_url", flat=True))
    
    if df is None or df.empty:
        print(f'el BOIB no existe')
    
    else:
        nuevos_anuncios = [
            AnuncioBoib(
                url_id=row["URL_id"],
                fecha=pd.to_datetime(row["Fecha"]).date(),
                boletin=row["Boletín"],
                numero_boletin=row["Número"],
                administracion=row["Administración"],
                entidad=row["Entidad"],
                texto_resolucion=row["Resolución"],
                link_pdf=row["PDF"],
                link_html=row["HTML"],
                link_xml=row["XML"],
                numero_registro=row["Nº Registro"],
                numero_url=row["Nº URL"],  # Clave única para evitar duplicados
            )
            for _, row in df.iterrows() if row["Nº URL"] not in urls_existentes
        ]

        if nuevos_anuncios:
            AnuncioBoib.objects.bulk_create(nuevos_anuncios)  # Inserta solo los nuevos

        return f"Se han insertado {len(nuevos_anuncios)} nuevos registros."

def get_max_url_id():
    """
    Devuelve el valor máximo de 'url_id' en la base de datos (el último boletín guardado en db).
    Si la tabla está vacía, retorna 12036.
    """
    max_url_id = AnuncioBoib.objects.aggregate(max_id=models.Max("url_id"))["max_id"]
    return max_url_id if max_url_id is not None else '12035'

def update_db():
    current_id = int(current_bulletin_id())
    max_url_id = int(get_max_url_id()) 
    print('El ultimo BOIB publicado es:', current_id)
    print('El ultimo BOIB guardado en DB es:', max_url_id)
    if current_id > max_url_id:
        while current_id > max_url_id:
            print(f'Actualizando BOIB: {str(max_url_id + 1)}')
            boib = BoibScraper(str(max_url_id + 1))
            df = boib.get_data()
            if df is None: 
                print('BOIB inexistente')
            else:
                dataframe_to_db(df)
                print(f'BOIB {max_url_id + 1} guardado con éxito')
            max_url_id += 1
        return f"BD actualizada! ID del último BOIB: {str(max_url_id) + 1}"

def anuncios_recientes(request):
    """Actualiza la base de datos y la vuelca en una tabla que se renderiza en
    'boib_scraper/anuncios.html'
    """
    #Actualiza la base de datos
    update_db()
    # Obtener la fecha de hace 20 días
    fecha_limite = now().date() - timedelta(days=30)
    # Filtrar los anuncios de los últimos 20 días y ordenarlos por fecha descendente
    anuncios = AnuncioBoib.objects.filter(fecha__gte=fecha_limite).order_by('-fecha')
    return render(request, 'boib_scraper/anuncios.html', {'anuncios': anuncios})