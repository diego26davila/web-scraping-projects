import scrapy, re    
import random
import requests                           
from urllib.parse import urlencode, urljoin     

API_KEY = ''   #crear una cuenta en Scraper API (u otro API) para obtener la clave de la API( scraperapi.com)  Scraper API brinda diferentes direcciones IP (proxyes) para poder realizar el scraping en sitios como Amazon.

def get_url(url):       #Modifica la url para conectar con la API
    payload = {'api_key': API_KEY, 'url': url, 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

class LinioSpider(scrapy.Spider):
    name = 'linio' 
        
    def start_requests(self):
        url = 'https://www.linio.com.pe/c/portatiles/laptops'
        yield scrapy.Request(url=url, callback=self.parse_laptop_list)
            
    def parse_laptop_list(self, response):
        laptop_name_paths = response.xpath('//div[@id="catalogue-product-container"]//a[@class="rating-container pill-enabled col-12 pl-0"]/@href').extract()  #se extraen todos los codigos de los productos del catalogo en la presente pagina
        for path in laptop_name_paths:
            laptop_url = f'https://www.linio.com.pe{path}'
            yield scrapy.Request(url=laptop_url, callback=self.parse_laptop_info, meta={'laptop_url': laptop_url})
            
        next_page_path = response.xpath('//a[@class="page-link page-link-icon"]/@href').extract_first()
        if next_page_path:
            next_page_url = urljoin('https://www.linio.com.pe',next_page_path)
            yield scrapy.Request(url=next_page_url, callback=self.parse_laptop_list)
            
    def parse_laptop_info(self, response):
        
        titulo = response.xpath('//div[@id="display-zoom"]//h1/span[@class="product-name"]/text()').extract()
        sku = response.xpath('//div[@id="panel-details"]//div[@itemprop="sku"]/text()').extract()
        precio = response.xpath('//div[@id="display-zoom"]//span[@class="price-main-md"]/text()').extract()
        laptop_url = [response.meta['laptop_url']]
        
        laptop_features = ['procesador',  'memoria', 'almacenamiento', 'sistema operativo', 'marca', 'tamaño de pantalla', 'resolución', 'medidas', 'peso', 'material', 'color', 'batería']
        
        feature_values = []
        for feature in laptop_features:
            feature_xpath = fr'//div[@id="panel-features"]//div[@class="product-bg-container"]//li[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"),"{feature}")]/text()'
            #feature_xpath += '"' + feature + '"'
            #feature_xpath += ')]/text()'
            
            feature_value = response.xpath(feature_xpath).extract()
            feature_values.append(feature_value)
            
        yield {'Laptop_Titulo': titulo,
               'Laptop_SKU': sku,
              'Laptop_Precio': precio,
              'Laptop_Url': laptop_url,
              'CPU_Modelo': feature_values[0],
               'RAM_Capacidad': feature_values[1],
               'DiscoDuro_Capacidad': feature_values[2],
               'SistemaOperativo': feature_values[3],
               'Laptop_Marca': feature_values[4],
               'Laptop_TPantalla': feature_values[5],
               'Laptop_RPantalla': feature_values[6],
               'Laptop_Dimensiones': feature_values[7],
               'Laptop_Peso': feature_values[8],
               'Laptop_Material': feature_values[9],
               'Laptop_Color': feature_values[10],
               'Laptop_Bateria': feature_values[11]
              }