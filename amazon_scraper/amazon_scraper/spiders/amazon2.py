import scrapy
from urllib.parse import urlencode

API_KEY = '62fc7b99ed9a7963c8606afdb3188481'
def get_url(url):
    payload = {'api_key': API_KEY, 'url': url, 'country_code': 'pe'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

# curl "http://api.scraperapi.com?api_key=62fc7b99ed9a7963c8606afdb3188481&url=https://www.amazon.com/dp/B094GB8JQL&country_code=pe"

class AmazonSpider(scrapy.Spider):
    name = 'laptops'
    
    def start_requests(self):
        
        urls = ['https://www.amazon.com/dp/B094GB8JQL',
                'https://www.amazon.com/dp/B08ZLFLF7L']
        
        for url in urls:
            yield scrapy.Request(url=get_url(url), callback=self.parse_product_page)

    def parse_keyword_response(self, response):
        products = response.xpath('//*[@data-asin]')
        for product in products:
            asin = product.xpath('@data-asin').extract_first()
            product_url = f'https://www.amazon.com/dp/{asin}'
            yield scrapy.Request(url=product_url, callback=self.parse_product_page, meta={'asin': asin})

    def parse_product_page(self, response):
        
        xp_title = '//*[@id="productTitle"]/text()'
        xp_precio_prod = '//div[contains(concat(" ",normalize-space(@id)," ")," corePrice_feature_div ")]//span[contains(concat(" ",normalize-space(@class)," ")," a-offscreen ")]/text()'
        xp_availability

        
        #asin = response.meta['asin']  
        title = response.xpath(xp_title).extract_first()
        precio_prod = response.xpath(xp_precio_prod).extract_first()
        
        availability = response.xpath()
        
        yield {'Title': title, 'Precio_Prod': precio_prod}
        
        
        
        
#//div[contains(concat(" ",normalize-space(@id)," ")," corePrice_desktop ")]//span[contains(concat(" ",normalize-space(@class)," ")," a-offscreen ")]/text()

#'//div[contains(concat(" ",normalize-space(@id)," ")," corePrice_feature_div ")]//span[contains(concat(" ",normalize-space(@class)," ")," a-offscreen ")]/text()'

#//div[contains(concat(" ",normalize-space(@class)," ")," celwidget ")]//div[contains(concat(" ",normalize-space(@class)," ")," celwidget ")]//div[contains(concat(" ",normalize-space(@class)," ")," celwidget ")]//span[contains(concat(" ",normalize-space(@class)," ")," a-price ")]//span[2]