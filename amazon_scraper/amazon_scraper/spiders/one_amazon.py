import scrapy
from urllib.parse import urlencode

API_KEY = 'd0f7996203a08327d1821be5ae8e9a9c'
def get_url(url):
    payload = {'api_key': API_KEY, 'url': url, 'country_code': 'pe'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

# curl "http://api.scraperapi.com?api_key=62fc7b99ed9a7963c8606afdb3188481&url=https://www.amazon.com/dp/B094GB8JQL&country_code=pe"

class AmazonSpider(scrapy.Spider):
    name = 'laptops'
    
    def start_requests(self):
        
        urls = ['https://www.amazon.com/dp/B08529BZSQ',
                'https://www.amazon.com/dp/B08XWLTKD1'] 
        
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
        xp_precio_prod = '//div[@id="corePrice_desktop"]//span[@class="a-offscreen"]/text()'
        xp_devblock = '//div[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]//*'
        xp_availability = '//div[@id="availability"]/span/text()'
        
        

        
        #asin = response.meta['asin']  
        title = response.xpath(xp_title).extract()
        precio_prod = response.xpath(xp_precio_prod).extract()
        len_precio_prod = [str(len(response.xpath(xp_precio_prod).extract()))]
        availability = response.xpath(xp_availability).extract()
        notif = [str(len(response.xpath(xp_devblock)))]
        
        if len(precio_prod) > 1:
            #PRECIO_BUSQUEDA_2
            precio_prod = response.xpath('//div[@id="corePrice_desktop"]//tr[2]//span[@class="a-offscreen"]/text()').extract()
        
        
        xp_desc = '//div[@id="productDescription"]//strong[contains(text(),"rocessor") or contains(text(), "CPU")]/parent::p/text()'
        desc = response.xpath(xp_desc).extract() 
        
        
        features_set = ['Processor', 'Processor Brand', 'Processor Count', 'Graphics Coprocessor', 'Card Description', 'Chipset Brand', 'Computer Memory Type', 'RAM', 'Hard Drive', 'Operating System', 'Brand', 'Series', 'Item model number', 'Standing screen display size', 'Screen Resolution', 'Item Weight', 'Item Dimensions LxWxH', 'Color', 'Average Battery Life (in hours)', 'Batteries']
        
        values_set = []
        for feature in features_set:   #Se busca el atributo en cada fila de la tabla
            xpath = "//table[@id='productDetails_techSpec_section_1' or @id='productDetails_techSpec_section_2']//th[normalize-space(text())="
            xpath += '"' + feature + '"'
            xpath += "]/following-sibling::td/text()"
            
            value = response.xpath(xpath).extract() 
            values_set.append(value)
        
        
    
        yield {'Title': title, 'Precio_Prod': precio_prod, 'len_precio': len_precio_prod, 'Availability': availability, 'Tiempo Entrega': notif,
               'CPU_Fabricante': values_set[1] , 
               'CPU_Nucleos': values_set[2],
               'GPU_Fabricante': values_set[3],
               'GPU_Tipo': values_set[4]}
 
        
        
        
        
#//div[contains(concat(" ",normalize-space(@id)," ")," corePrice_desktop ")]//span[contains(concat(" ",normalize-space(@class)," ")," a-offscreen ")]/text()

#'//div[contains(concat(" ",normalize-space(@id)," ")," corePrice_feature_div ")]//span[contains(concat(" ",normalize-space(@class)," ")," a-offscreen ")]/text()'

#//div[contains(concat(" ",normalize-space(@class)," ")," celwidget ")]//div[contains(concat(" ",normalize-space(@class)," ")," celwidget ")]//div[contains(concat(" ",normalize-space(@class)," ")," celwidget ")]//span[contains(concat(" ",normalize-space(@class)," ")," a-price ")]//span[2]

# xp_devblock = len('//dev[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]//*')
# xp_availability = '//dev[@id="availability"]/span/text()'


