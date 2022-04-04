import scrapy, re 
import random, requests                             
from urllib.parse import urlencode, urljoin     

#luego de correr el contenedor de cloudproxy, se realiza el request a http://localhost:8000

#def random_proxy():
#    ips = requests.get("http://localhost:8000").json()
#    return random.choice(ips['ips'])

#headers = { 'proxies': {"http": random_proxy(), "https": random_proxy()}}

#API_KEY = 'd0f7996203a08327d1821be5ae8e9a9c'   #crear una cuenta en Scraper API (u otro API) para obtener la clave de la API( scraperapi.com)  Scraper API brinda diferentes direcciones IP (proxyes) para poder realizar el scraping en sitios como Amazon.

#def get_url(url):       #Modifica la url para conectar con la API
#    payload = {'api_key': API_KEY, 'url': url, 'country_code': 'us'}
#    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
#    return proxy_url

queries = ['laptops']    #Se realizará la busqueda solo de laptops. Pueden agregarse más a la lista. Pero cuidado con los limites del plan gratis de Scraper API (5000 requests por mes)

class AmazonSpider(scrapy.Spider):
    name = 'amazon2'      #Nombre del spider. Se utilizara para correr el codigo luego
    
    def start_requests(self):       #Se generan las solicitudes
        for query in queries:
            url = 'https://www.amazon.com/s?' + urlencode({'k': query })    #se construye la url para acceder a la pagina del catalogo
            yield scrapy.Request(url=url, callback=self.parse_keyword_response) 
            
    def parse_keyword_response(self, response):
        products = response.xpath('//*[@data-asin]')  #se extraen todos los codigos de los productos del catalogo en la presente pagina
        for product in products:
            codigo = product.xpath('@data-asin').extract_first()           
            product_url = f'https://www.amazon.com/dp/{codigo}'        #se construye la url para acceder a la página de cada producto
            yield scrapy.Request(url=product_url, callback=self.parse_product_page, meta={'codigo': codigo}) 
            # La respuesta del Request se envia a la funcion callback 'parse_product_page' con la metadata
            
        next_page = response.xpath('//div[@class="a-section a-text-center s-pagination-container"]//a[@class = "s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]/@href').extract_first()  #se busca si hay una pagina siguiente
        if next_page:
            print(f'TURNING TO NEXT PAGE')
            next_url = urljoin('https://www.amazon.com',next_page) #se construye la url de la siguiente pagina
            yield scrapy.Request(url=next_url, callback=self.parse_keyword_response)   
            #se crea un nuevo request para extraer la informacion de la siguiente pagina

    def parse_product_page(self, response):
        
        codigo = [response.meta['codigo']]     #el codigo recibido del Request como metadata
        titulo = response.xpath('//h1[@id="title"]/span[@id="productTitle"]/text()').extract()  #el titulo extenso del producto, ayudará luego a obtener datos de la RAM y del disco duro
        if titulo == []:
            return

        marca_cpu = re.findall('(?i)(intel|amd)',titulo[0])
        marca_cpu = list(set(i.upper() for i in marca_cpu))
        if len(marca_cpu) != 1:
            marca_cpu = response.xpath('//table[@id="productDetails_techSpec_section_2"]//th[contains(text(),"Processor Brand")]/following-sibling::td/text()').extract()
            if marca_cpu != []:
                marca_cpu = [marca_cpu[0].upper()]
            else:
                marca_cpu = ['NO MARCAAAAAA']

        if marca_cpu == ['INTEL']:
            match_modelo = re.findall(r'(?i)i\d+[\s-]*\d+|\d+[th\s]*gen.*i\d+', titulo[0])
            if match_modelo != []:
                cpu_modelo = [match_modelo[0]]
            else:
                match_modelo = re.findall(r'(?i)celeron|xeon|pentium', titulo[0])
                if match_modelo != []:
                    cpu_modelo = match_modelo
                else:
                    cpu_modelo = ['OTHER INTEL CPU']      
        else:
            cpu_modelo = ['FALTAAAA']


        costo_laptop = response.xpath('//div[@id="exportsBuybox"]//span[contains(text(),"$")]/text()').extract()
        if costo_laptop != []:
            costo_laptop = [costo_laptop[0]]
        listprice_laptop = response.xpath('//div[@id="corePrice_desktop"]//*[contains(text(),"List Price")]/following-sibling::*//*[@class="a-offscreen"]/text()').extract()
        
        costo_envio_dep = []
        delivery_date = []
        availability = ['NO PERU']
        delivery_noperu = response.xpath('//div[@id="mir-layout-DELIVERY_BLOCK"]//span[contains(@class,"a-color-error")]').extract()
        if delivery_noperu == []:
            costo_envio_dep = response.xpath('//div[@id="exports_desktop_qualifiedBuybox_tlc_feature_div"]//span[@class="a-size-base a-color-secondary"]/text()').extract()

            delivery_date = response.xpath('//div[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]//span[@class="a-text-bold"]/text()').extract()
                
            availability = response.xpath('//div[@id="availability"]/span/text()').extract()


        yield {'Laptop_Codigo': codigo, 
               'Laptop_Nombre': titulo,
               'Precio_Laptop': costo_laptop,
               'PrecioLista_Laptop': listprice_laptop,
               'Costo_Envio_Dep': costo_envio_dep,
               'CPU_Marca': marca_cpu,
               'CPU_Modelo': cpu_modelo,
               'Fecha_Delivery': delivery_date,
               'Stock': availability
               }
