import scrapy
from urllib.parse import urlencode

""" API_KEY = '62fc7b99ed9a7963c8606afdb3188481'
def get_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url """

queries = ['laptops']

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    
    def start_requests(self):
        for query in queries:
            url = 'https://www.amazon.com/s?' + urlencode({'k': query })
            proxy_url = 'http://64.235.204.107:3128'
            yield scrapy.Request(url, callback=self.parse_keyword_response, meta={ 'proxy': proxy_url })
            
    def parse_keyword_response(self, response):
        products = response.xpath('//*[@data-asin]')
        for product in products:
            codigo = product.xpath('@data-asin').extract_first()           #codigo unico 'asin' del producto en el catalogo de amazon
            product_url = f'https://www.amazon.com/dp/{codigo}'
            yield scrapy.Request(url=product_url, callback=self.parse_product_page, meta={'codigo': codigo}) 
            # la variable codigo se pasa a la funcion callback 'parse_product_page' como el parametro 'codigo'

    def parse_product_page(self, response):
        codigo = response.meta['codigo']               #el parametro 'codigo' se almacena en una nueva variable codigo
        titulo = response.xpath('//*[@id="productTitle"]/text()').extract_first()    #se extrael del html el nombre del producto
        precio = response.xpath('//div[@id="corePrice_feature_div"]//span[@class="a-offscreen"/text()]')  #se extrae el precio
        yield {'Codigo_Prod': codigo, 'Nombre_Prod': titulo, 'Precio': precio}
        
        
