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
        
        urls = ['https://www.amazon.com/dp/B09N6XTV4S',
                'https://www.amazon.com/dp/B09Q5H4S91'] 
        
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
        xp_precio_prod = '//div[@id="corePrice_feature_div"]//span[@class="a-offscreen"]/text()'
        xp_devblock = '//dev[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]//*'
        xp_availability = '//dev[@id="availability"]/span/text()'
        
        

        
        #asin = response.meta['asin']  
        title = response.xpath(xp_title).extract_first()
        precio_prod = response.xpath(xp_precio_prod).extract_first()
        availability = response.xpath(xp_availability).extract()
        notif = len(response.xpath(xp_devblock))
        
        xp_desc = '//div[@id="productDescription"]//strong[contains(text(),"rocessor") or contains(text(), "CPU")]/parent::p/text()'
        xp_desc_cpu2 = '//div[@id="productDescription"]/p//*[contains(text(),"rocessor") or contains(text(),"CPU")]/text()'

        
        
        
        desc = response.xpath(xp_desc).extract() 
        
        
    
        yield {'Title': title, 'Precio_Prod': precio_prod, 'Availability': availability, 'Tiempo Entrega': notif, 
               'td0': type(desc[0]),
               'td1': type(desc),
               'td2': type(desc),
               'td3': type(desc),
               'td4': type(desc)
              ## 'td5': desc[5],
               ##'td6': desc[6],
               #'td7': desc[7],
               #'td8': desc[8]
              }
 
        
        
        
        
#//div[contains(concat(" ",normalize-space(@id)," ")," corePrice_desktop ")]//span[contains(concat(" ",normalize-space(@class)," ")," a-offscreen ")]/text()

#'//div[contains(concat(" ",normalize-space(@id)," ")," corePrice_feature_div ")]//span[contains(concat(" ",normalize-space(@class)," ")," a-offscreen ")]/text()'

#//div[contains(concat(" ",normalize-space(@class)," ")," celwidget ")]//div[contains(concat(" ",normalize-space(@class)," ")," celwidget ")]//div[contains(concat(" ",normalize-space(@class)," ")," celwidget ")]//span[contains(concat(" ",normalize-space(@class)," ")," a-price ")]//span[2]

# xp_devblock = len('//dev[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]//*')
# xp_availability = '//dev[@id="availability"]/span/text()'


        #3)
        if desc_cpu == [] and desc_gpu == [] and desc_ram == [] and desc_disc == []:

            xp_desc = '//div[@id="productDescription"]/p//text()'
            xp_desc_cpu2 = '//div[@id="productDescription"]/p//*[contains(text(),"rocessor") or contains(text(),"CPU")]/text()'
            xp_desc_gpu2 = '//div[@id="productDescription"]/p//*[contains(text(),"raphics")]/text()'
            xp_desc_ram2 = '//div[@id="productDescription"]/p//*[contains(text(),"Memory")]/text()'
            xp_desc_disc2 = '//div[@id="productDescription"]/p//*[contains(text(),"Hard ") or contains(text(), "torage")]/text()'
           
            desc = response.xpath(xp_desc).extract()        

            texto_header = response.xpath(xp_desc_cpu2).extract_first()
            if texto_header:
                desc_cpu = [desc[desc.index(texto_header) + 1]]
        
            texto_header = response.xpath(xp_desc_gpu2).extract_first()
            if texto_header:
                desc_gpu = [desc[desc.index(texto_header) + 1]]
  
            texto_header = response.xpath(xp_desc_ram2).extract_first()
            if texto_header:
                desc_ram = [desc[desc.index(texto_header) + 1]]
             
            texto_header = response.xpath(xp_desc_disc2).extract_first()
            if texto_header:
                desc_disc = [desc[desc.index(texto_header) + 1]]
