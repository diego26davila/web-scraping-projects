import scrapy, re                              
from urllib.parse import urlencode, urljoin     

API_KEY = 'd0f7996203a08327d1821be5ae8e9a9c'   #crear una cuenta en Scraper API (u otro API) para obtener la clave de la API( scraperapi.com)  Scraper API brinda diferentes direcciones IP (proxyes) para poder realizar el scraping en sitios como Amazon.

def get_url(url):       #Modifica la url para conectar con la API
    payload = {'api_key': API_KEY, 'url': url, 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

queries = ['laptops']    #Se realizará la busqueda solo de laptops. Pueden agregarse más a la lista. Pero cuidado con los limites del plan gratis de Scraper API (5000 requests por mes)

class AmazonSpider(scrapy.Spider):
    name = 'amazon'      #Nombre del spider. Se utilizara para correr el codigo luego
    
    def start_requests(self):       #Se generan las solicitudes
        for query in queries:
            url = 'https://www.amazon.com/s?' + urlencode({'k': query })    #se construye la url para acceder a la pagina del catalogo
            yield scrapy.Request(get_url(url), callback=self.parse_keyword_response) 
            
    def parse_keyword_response(self, response):
        products = response.xpath('//*[@data-asin]')  #se extraen todos los codigos de los productos del catalogo en la presente pagina
        for product in products:
            codigo = product.xpath('@data-asin').extract_first()           
            product_url = f'https://www.amazon.com/dp/{codigo}'        #se construye la url para acceder a la página de cada producto
            yield scrapy.Request(url=get_url(product_url), callback=self.parse_product_page, meta={'codigo': codigo}) 
            # La respuesta del Request se envia a la funcion callback 'parse_product_page' con la metadata
            
        next_page = response.xpath('//div[@class="a-section a-text-center s-pagination-container"]//a[@class = "s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]/@href').extract_first()  #se busca si hay una pagina siguiente
        if next_page:
            next_url = urljoin('https://www.amazon.com',next_page) #se construye la url de la siguiente pagina
            yield scrapy.Request(url=get_url(next_url), callback=self.parse_keyword_response)   
            #se crea un nuevo request para extraer la informacion de la siguiente pagina

    def parse_product_page(self, response):
        
        codigo = [response.meta['codigo']]        #el codigo recibido del Request como metadata
        titulo = response.xpath('//*[@id="productTitle"]/text()').extract()  #el titulo extenso del producto, ayudará luego a obtener datos de la RAM y del disco duro
        
        #---------------------------
        
        #PRECIO_BUSQUEDA_1
        precio = response.xpath('//div[@id="corePrice_desktop"]//span[@class="a-offscreen"]/text()').extract() # el método extract() retorna una lista de len() >= 1
        
        if len(precio) > 1:
            
            #PRECIO_BUSQUEDA_2
            precio = response.xpath('//div[@id="corePrice_desktop"]//tr[2]//span[@class="a-offscreen"]/text()').extract()
            
        if not precio:   #si extract() no encuentra resultado retorna None (type 'Nonetype')
            
            #PRECIO_BUSQUEDA_3
            xp_price_whole = '//div[@id="corePriceDisplay_desktop_feature_div"]//span[@class="a-price-whole"]/text()'
            xp_price_fraction = '//div[@id="corePriceDisplay_desktop_feature_div"]//span[@class="a-price-fraction"]/text()'
            precio_ent = response.xpath(xp_price_whole).extract_first()  #el metodo extract_first() retorna data de tipo 'str'
            precio_frac = response.xpath(xp_price_fraction).extract_first()
            
            if precio_ent and precio_frac:
                precio = [str(int(precio_ent.replace(',','')) + int(precio_frac)/100)]   #se reemplaza la ',' de los miles (e.g 1,234), se junta el precio entero y fraccion, y se encierra en [] para crear una lista de len() = 1 (todas las variables respuesta se pasaran de este modo)
                
        #-------------------------
        #CARACTERÍSTICAS DEL PRODUCTO
        
        #De cada pagina del producto se extraera estos atributos
        features_set = ['Processor', 'Processor Brand', 'Processor Count', 'Graphics Coprocessor', 'Card Description', 'Chipset Brand', 'Computer Memory Type', 'RAM', 'Hard Drive', 'Operating System', 'Brand', 'Series', 'Item model number', 'Standing screen display size', 'Screen Resolution', 'Item Weight', 'Item Dimensions LxWxH', 'Color', 'Average Battery Life (in hours)', 'Batteries']
        
        values_set = []
        for feature in features_set:   #Se busca el atributo en cada fila de la tabla
            xpath = "//table[@id='productDetails_techSpec_section_1' or @id='productDetails_techSpec_section_2']//th[normalize-space(text())="
            xpath += '"' + feature + '"'
            xpath += "]/following-sibling::td/text()"
            
            value = response.xpath(xpath).extract() 
            values_set.append(value)    #Lista con todos los valores de los atributos
            
        #Los datos obtenidos en la busqueda anterior no están completos para todos los productos, por ello se realizan otras búsquedas más para algunos atributos de la laptop
        
        #---------------------------
        #OTRAS BUSQUEDAS COMPLEMENTARIAS
        
        desc_cpu = []
        desc_gpu = []
        desc_ram = []
        desc_disc = []
        
        
        xp_desc = '//div[@id="productDescription"]/p//text()'
        desc = response.xpath(xp_desc).extract()  
        
        xp_desc_cpu4 = '//div[@id="productDescription"]/p//*[contains(text(),"rocessor") or contains(text(),"CPU")]/text()'
        texto_header = response.xpath(xp_desc_cpu4).extract_first()
        if texto_header:
            desc_cpu = [desc[desc.index(texto_header) + 1]]
        
        xp_desc_gpu4 = '//div[@id="productDescription"]/p//*[contains(text(),"raphics") or contains(text(),"ideo:")]/text()'
        texto_header = response.xpath(xp_desc_gpu4).extract_first()
        if texto_header:
            desc_gpu = [desc[desc.index(texto_header) + 1]]
        
        xp_desc_ram4 = '//div[@id="productDescription"]/p//*[contains(text(),"Memory")]/text()'
        texto_header = response.xpath(xp_desc_ram4).extract_first()
        if texto_header:
            desc_ram = [desc[desc.index(texto_header) + 1]]
        
        xp_desc_disc4 = '//div[@id="productDescription"]/p//*[contains(text(),"Hard ") or contains(text(), "torage")]/text()'
        texto_header = response.xpath(xp_desc_disc4).extract_first()
        if texto_header:
            if len(texto_header.split()) <= 2:
                desc_disc = [desc[desc.index(texto_header) + 1]]
            else:
                desc_disc = [desc[desc.index(texto_header)]]
                
        #1)
        if desc_cpu == []:
            xp_desc_cpu1 = '//div[@id="productDescription"]//strong[contains(text(),"rocessor") or contains(text(), "CPU")]/parent::p/text()'
            desc_cpu = response.xpath(xp_desc_cpu1).extract()
        
        if desc_gpu == []:
            xp_desc_gpu1 = '//div[@id="productDescription"]//strong[contains(text(),"raphics") or contains(text(),"ideo:")]/parent::p/text()'
            desc_gpu = response.xpath(xp_desc_gpu1).extract()
            
        if desc_ram == []:
            xp_desc_ram1 = '//div[@id="productDescription"]//strong[contains(text(),"Memory")]/parent::p/text()'
            desc_ram = response.xpath(xp_desc_ram1).extract()
            
        if desc_disc == []:
            xp_desc_disc1 = '//div[@id="productDescription"]//strong[contains(text(),"Hard ") or contains(text(), "torage")]/parent::p/text()'
            desc_disc = response.xpath(xp_desc_disc1).extract()
        
        
        #2)
        
        if desc_cpu == [] and desc_gpu == [] and desc_ram == [] and desc_disc == []:
            xp_desc_cpu3 = '//div[@id="productDescription"]//b[contains(text(),"rocessor") or contains(text(), "CPU")]/parent::li/text()'
            xp_desc_gpu3 = '//div[@id="productDescription"]//b[contains(text(),"raphics") or contains(text(),"ideo:")]/parent::li/text()'
            xp_desc_ram3 = '//div[@id="productDescription"]//b[contains(text(),"Memory")]/parent::li/text()'
            xp_desc_disc3 = '//div[@id="productDescription"]//b[contains(text(),"Hard ") or contains(text(), "torage")]/parent::li/text()'

            desc_cpu = response.xpath(xp_desc_cpu3).extract()
            desc_gpu = response.xpath(xp_desc_gpu3).extract()
            desc_ram = response.xpath(xp_desc_ram3).extract()
            desc_disc = response.xpath(xp_desc_disc3).extract()

    

        
        #--------------------------
        #De los resultados de las busquedas se separan algunos datos importantes para el análisis
        #DATOS_CPU
        
        cpu = []
        if values_set[0] != []:
            cpu = re.findall('(?<=GHz)\s*\w+\d*',values_set[0][0])
        
        

        #DATOS_MEMORIA_RAM
        
        ram_gb = []
        ram_gen = []   
        if values_set[7] != []:   #Se extrae del valor del atributo 'RAM' (values_set[7]) Solo la capacidad en GB y el tipo de RAM
            value = values_set[7][0]
            ram_gb = [re.findall('[0-9]+', value)[0]]  #Se utilizan 'regular expressions - regex' para extraer el texto deseado
            ram_gen = re.findall('(?i)(?<=gb).*DDR.*', value)
            
            if ram_gen == []:     #Si no se encuentra el tipo de RAM se extrae este dato del valor del atributo 'Computer Memory Type' (values_Set[7])
                if values_set[6] != []:   
                    ram_gen = re.findall('.*DDR\w*',values_set[6][0])
                    if ram_gen == []:
                        ram_gen = [re.findall('\w+',values_set[6][0])[0] + '(Verificar)']
            
        
        #-------------------------
        
        #DATOS_DISCO_DURO
        
        
        
        tipo_disco = []
        if titulo != []:
            match_tipo_disco = re.findall('(?i)emmc|ssd|hdd', titulo[0])
            if len(match_tipo_disco) > 1: 
                tipo_disco = 'Hybrid'
            else: 
                tipo_disco = match_tipo_disco
            
        elif values_set[8] != []:
            tipo_disco = [re.findall('(?i)(?<=gb|tb).*', values_set[8][0])[0] + '(Verificar)']
            if tipo_disco == []:
                tipo_disco = [values_set[8][0] + '(Verificar)']
        
        match_result1 = []
        if titulo != []:
            match_result1 = re.findall('(?i)(\d+)\s*(gb|tb)', titulo[0])    #Del titulo se extraera los datos del disco duro
            

        match_result2 = []    
        if values_set[8] != []:    
            match_result2 = re.findall('([1-9]+)\s*(GB|TB)', values_set[8][0]) #Se extrae el valor del atributo 'Hard Drive' (values_set[9])


        if match_result1 != []:
            
            num_value = []
            for i in match_result1:
                if i[1] == 'TB' or i[1] == 'tb':
                    value = int(i[0])*1000
                    num_value.append(value)
                else:
                    value = int(i[0])
                    num_value.append(int(value))

            index_maxnum = num_value.index(max(num_value))
            disco_gb = num_value[index_maxnum]
            
            if ram_gb != []: 
                if disco_gb > int(ram_gb[0]):
                    disco_cap = [match_result1[index_maxnum][0] + ' ' + match_result1[index_maxnum][1]]
                else:
                    disco_cap = [match_result1[index_maxnum][0] + ' ' + match_result1[index_maxnum][1] + '(Verificar)']
            else:
                disco_cap = [match_result1[index_maxnum][0] + ' ' + match_result1[index_maxnum][1] + '(Verificar)']
                
        elif match_result2 != []:
    
            i = match_result2[0]
            if i[1] == 'TB' or i[1] == 'tb':
                disco_gb = int(i[0])*1000
            else:
                disco_gb = int(i[0])
            
            if ram_gb != []: 
                if disco_gb > int(ram_gb[0]): 
                    disco_cap = [match_result2[0][0] + ' ' + match_result2[0][1]]
                else:
                    disco_cap = [match_result2[0][0] + ' ' + match_result2[0][1] + '(Verificar)']
            else:
                disco_cap = [match_result2[0][0] + ' ' + match_result2[0][1] + '(Verificar)']
                
        else:
             disco_cap = []
                
                
        yield {'Laptop_Codigo': codigo, 
               'Laptop_Nombre': titulo, 
               'Laptop_Precio': precio, 
               'CPU_Modelo': cpu,
               'CPU_Fabricante': values_set[1] , 
               'CPU_Nucleos': values_set[2],
               'CPU_Descripcion': desc_cpu,
               'GPU_Fabricante': values_set[3],
               'GPU_Tipo': values_set[4],
               'GPU_Descripcion': desc_gpu,
               'Chipset_Fabricante': values_set[5],
               'RAM_Capacidad': ram_gb,
               'RAM_Tipo': values_set[6],
               'RAM_Generacion': ram_gen,
               'RAM_Descripcion': desc_ram,
               'DiscoDuro_Capacidad': disco_cap,
               'DiscoDuro_Tipo': tipo_disco,
               'DiscoDuro_Descripcion': desc_disc,
               'Sistema_Operativo': values_set[9],
               'Laptop_Marca': values_set[10],
               'Laptop_Serie': values_set[11],
               'Laptop_Modelo': values_set[12],
               'Laptop_TPantalla': values_set[13],
               'Laptop_RPantalla': values_set[14],
               'Laptop_Peso': values_set[15],
               'Laptop_Dimensiones': values_set[16],
               'Laptop_Color': values_set[17],
               'Laptop_DBateria': values_set[18],
               'Laptop_DBateria': values_set[19]}
        
        
        
    

