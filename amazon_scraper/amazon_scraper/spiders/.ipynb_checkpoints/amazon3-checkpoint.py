import scrapy, re                              
from urllib.parse import urlencode, urljoin     

API_KEY = 'd0f7996203a08327d1821be5ae8e9a9c'   #crear una cuenta en Scraper API (u otro API) para obtener la clave de la API( scraperapi.com)  Scraper API brinda diferentes direcciones IP (proxyes) para poder realizar el scraping en sitios como Amazon.

def get_url(url):       #Modifica la url para conectar con la API
    payload = {'api_key': API_KEY, 'url': url, 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

queries = ['laptops']    #Se realizará la busqueda solo de laptops. Pueden agregarse más a la lista. Pero cuidado con los limites del plan gratis de Scraper API (5000 requests por mes)

class AmazonSpider(scrapy.Spider):
    name = 'amazon2'      #Nombre del spider. Se utilizara para correr el codigo luego
    
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
            print(f'TURNING TO NEXT PAGE')
            next_url = urljoin('https://www.amazon.com',next_page) #se construye la url de la siguiente pagina
            yield scrapy.Request(url=get_url(next_url), callback=self.parse_keyword_response)   
            #se crea un nuevo request para extraer la informacion de la siguiente pagina

    def parse_product_page(self, response):
        
        codigo_list = [response.meta['codigo']]        #el codigo recibido del Request como metadata
        titulo_list = response.xpath('//*[@id="productTitle"]/text()').extract()  #el titulo extenso del producto, ayudará luego a obtener datos de la RAM y del disco duro
        
        #---------------------------
        
        #PRECIO_BUSQUEDA_1
        precio_list = response.xpath('//div[@id="corePrice_desktop"]//span[@class="a-offscreen"]/text()').extract() # el método extract() retorna una lista de len() >= 1
        
        if len(precio_list) > 1:
            precio_list = [precio_list[0]]
            #PRECIO_BUSQUEDA_2
            if precio_list == []:
                precio_list = response.xpath('//div[@id="corePrice_desktop"]//tr[2]//span[@class="a-offscreen"]/text()').extract()
            
            
        if precio_list == []:   #si extract() no encuentra resultado retorna [] (type 'list')
            
            #PRECIO_BUSQUEDA_3
            xp_price_whole = '//div[@id="corePriceDisplay_desktop_feature_div"]//span[@class="a-price-whole"]/text()'
            xp_price_fraction = '//div[@id="corePriceDisplay_desktop_feature_div"]//span[@class="a-price-fraction"]/text()'
            precio_ent = response.xpath(xp_price_whole).extract_first()  #el metodo extract_first() retorna data de tipo 'str'
            precio_frac = response.xpath(xp_price_fraction).extract_first()
            
            if precio_ent and precio_frac:
                precio_list = [str(int(precio_ent.replace(',','')) + int(precio_frac)/100)]   #se reemplaza la ',' de los miles (e.g 1,234), se junta el precio entero y fraccion, y se encierra en [] para crear una lista de len() = 1 (todas las variables respuesta se pasaran de este modo)
                
        #-------------------------
        #CARACTERÍSTICAS DEL PRODUCTO
        
        #De cada pagina del producto se extraera estos atributos
        features_list = ['Processor', 'Processor Brand', 'Processor Count', 'Graphics Coprocessor', 'Card Description', 'Chipset Brand', 'Computer Memory Type', 'RAM', 'Hard Drive', 'Operating System', 'Brand', 'Series', 'Item model number', 'Standing screen display size', 'Screen Resolution', 'Item Weight', 'Item Dimensions LxWxH', 'Color', 'Batteries']
        
        values_list = []
        for feature in features_list:   #Se busca el atributo en cada fila de la tabla
            xpath = "//table[@id='productDetails_techSpec_section_1' or @id='productDetails_techSpec_section_2']//th[normalize-space(text())="
            xpath += '"' + feature + '"'
            xpath += "]/following-sibling::td/text()"
            
            value = response.xpath(xpath).extract() 
            values_list.append(value)    #Lista con todos los valores de los atributos
        
        cpu_model_info = values_list[0]
        cpu_fab_info = values_list[1]
        cpu_nucleo_info = values_list[2]
        gpu_fab_info = values_list[3]
        gpu_tipo_info = values_list[4]
        chipset_info = values_list[5]
        ram_tipo_info = values_list[6]
        ram_gen_info = values_list[7]
        disco_info = values_list[8]
        sis_op_info = values_list[9]
        marca_info = values_list[10]
        serie_info = values_list[11]
        model_info = values_list[12]
        pulg_info = values_list[13]
        resol_info = values_list[14]
        peso_info = values_list[15]
        dim_info = values_list[16]
        color_info = values_list[17]
        bate_info = values_list[18]
        
        #Los datos obtenidos en la busqueda anterior no están completos para todos los productos, por ello se realizan otras búsquedas más para algunos atributos de la laptop
        
        #---------------------------
        #OTRAS BUSQUEDAS COMPLEMENTARIAS
        #1)
        desc_cpu_list = []
        desc_gpu_list = []
        desc_ram_list = []
        desc_disc_list = []
    
        xp_desc = '//div[@id="productDescription"]/p//text()'
        desc_list = response.xpath(xp_desc).extract()  
        
        xp_desc_cpu1 = '//div[@id="productDescription"]/p//*[contains(text(),"rocessor") or contains(text(),"CPU")]/text()'
        texto_header = response.xpath(xp_desc_cpu1).extract_first()
        if texto_header:
            desc_cpu_list = [desc_list[desc_list.index(texto_header) + 1]]
        
        xp_desc_gpu1 = '//div[@id="productDescription"]/p//*[contains(text(),"raphics") or contains(text(),"ideo:")]/text()'
        texto_header = response.xpath(xp_desc_gpu1).extract_first()
        if texto_header:
            desc_gpu_list = [desc_list[desc_list.index(texto_header) + 1]]
        
        xp_desc_ram1 = '//div[@id="productDescription"]/p//*[contains(text(),"Memory")]/text()'
        texto_header = response.xpath(xp_desc_ram1).extract_first()
        if texto_header:
            desc_ram_list = [desc_list[desc_list.index(texto_header) + 1]]
        
        xp_desc_disc1 = '//div[@id="productDescription"]/p//*[contains(text(),"Hard ") or contains(text(), "torage")]/text()'
        texto_header = response.xpath(xp_desc_disc1).extract_first()
        if texto_header:
            if len(texto_header.split()) <= 2:
                desc_disc_list = [desc_list[desc_list.index(texto_header) + 1]]
            else:
                desc_disc_list = [desc_list[desc_list.index(texto_header)]]
                
        #2)
        if desc_cpu_list == [] or desc_cpu_list == [':']:
            xp_desc_cpu2 = '//div[@id="productDescription"]//strong[contains(text(),"rocessor") or contains(text(), "CPU")]/parent::p/text()'
            desc_cpu_list = response.xpath(xp_desc_cpu2).extract()
        
        if desc_gpu_list == [] or desc_gpu_list == [':']:
            xp_desc_gpu2 = '//div[@id="productDescription"]//strong[contains(text(),"raphics") or contains(text(),"ideo:")]/parent::p/text()'
            desc_gpu_list = response.xpath(xp_desc_gpu2).extract()
            
        if desc_ram_list == [] or desc_ram_list == [':']:
            xp_desc_ram2 = '//div[@id="productDescription"]//strong[contains(text(),"Memory")]/parent::p/text()'
            desc_ram_list = response.xpath(xp_desc_ram2).extract()
            
        if desc_disc_list == [] or desc_disc_list == [':']:
            xp_desc_disc2 = '//div[@id="productDescription"]//strong[contains(text(),"Hard ") or contains(text(), "torage")]/parent::p/text()'
            desc_disc_list = response.xpath(xp_desc_disc2).extract()
        
        #3)
        if desc_cpu_list == []:
            xp_desc_cpu3 = '//div[@id="feature-bullets"]//li//*[contains(text(),"rocessor") or contains(text(), "CPU")]/text()'
            desc_cpu_list = response.xpath(xp_desc_cpu3).extract()
        
        if desc_gpu_list == []:
            xp_desc_gpu3 = '//div[@id="feature-bullets"]//li//*[contains(text(),"raphics") or contains(text(),"GPU")]/text()'
            desc_gpu_list = response.xpath(xp_desc_gpu3).extract()
            
        if desc_ram_list == []:
            xp_desc_ram3 = '//div[@id="feature-bullets"]//li//*[contains(text(),"emory") or contains(text(),"RAM")]/text()'
            desc_ram_list = response.xpath(xp_desc_ram3).extract()
            
        if desc_disc_list == []:
            xp_desc_disc3 = '//div[@id="feature-bullets"]//li//*[contains(text(),"Hard ") or contains(text(), "torage") or contains(text(), "olid")]/text()'
            desc_disc_list = response.xpath(xp_desc_disc3).extract()
        
        #4)
        if desc_cpu_list == [] and desc_gpu_list == [] and desc_ram_list == [] and desc_disc_list == []:
            xp_desc_cpu4 = '//div[@id="productDescription"]//b[contains(text(),"rocessor") or contains(text(), "CPU")]/parent::li/text()'
            xp_desc_gpu4 = '//div[@id="productDescription"]//b[contains(text(),"raphics") or contains(text(),"ideo:")]/parent::li/text()'
            xp_desc_ram4 = '//div[@id="productDescription"]//b[contains(text(),"Memory")]/parent::li/text()'
            xp_desc_disc4 = '//div[@id="productDescription"]//b[contains(text(),"Hard ") or contains(text(), "torage")]/parent::li/text()'

            desc_cpu_list = response.xpath(xp_desc_cpu4).extract()
            desc_gpu_list = response.xpath(xp_desc_gpu4).extract()
            desc_ram_list = response.xpath(xp_desc_ram4).extract()
            desc_disc_list = response.xpath(xp_desc_disc4).extract()

                
        #--------------------------
        #De los resultados de las busquedas se separan algunos datos importantes para el análisis
        #DATOS_CPU
        
        cpu_model_list = []
        corei_num_list = ['-']
        corei_gen_list = ['-']
        if titulo_list != []:
            find_ryzen_cpu = re.findall(r'(?i)ryzen', titulo_list[0])
            if find_ryzen_cpu != []:
                cpu_model_list = []
            else:          
                find_intelcore_cpu = re.findall(r'(?i)i3-*\s*\d+|i5-*\s*\d+|i7-*\s*\d+|i9-*\s*\d+',titulo_list[0])
                cpu_model_list = find_intelcore_cpu
                if find_intelcore_cpu != [] and len(find_intelcore_cpu) > 1:
                    cpu_model_list = [find_intelcore_cpu[0]]
                if cpu_model_list != []:
                    corei_num_list = re.findall(r'(?i)i3|i5|i7|i9', cpu_model_list[0])
                    corei_gen_list = re.findall(r'(?i)(?<=i\d-)1\d|(?<=i\d-)[2-9]|(?<=i\d )1\d|(?<=i\d )[5-9]', cpu_model_list[0])
                
        if cpu_model_list == [] and titulo_list != []:
            find_ryzen_cpu = re.findall(r'(?i)ryzen', titulo_list[0])
            if find_ryzen_cpu != []:
                cpu_model_list = []
            elif desc_cpu_list != []:
                find_intelcore_cpu = re.findall(r'(?i)i3-*\s*\d+|i5-*\s*\d+|i7-*\s*\d+|i9-*\s*\d+', desc_cpu_list[0])
                cpu_model_list = find_intelcore_cpu
                if find_intelcore_cpu != [] and len(find_intelcore_cpu) > 1:
                    cpu_model_list = [find_intelcore_cpu[0]]
                if cpu_model_list != []:
                    corei_num_list = re.findall(r'(?i)i3|i5|i7|i9', cpu_model_list[0])
                    corei_gen_list = re.findall(r'(?i)(?<=i\d-)1\d|(?<=i\d-)[2-9]|(?<=i\d )1\d|(?<=i\d )[5-9]', cpu_model_list[0])
                
        if cpu_model_list == [] and cpu_model_info != []:
            cpu_model_list = re.findall('(?i)(?<=ghz)\s*\w+\d*|(?<=hertz)\s*\w+\d*',cpu_model_info[0])
            if cpu_model_list == []:
                cpu_model_list = cpu_model_info
    
        cpu_nucleo_list = []
        cpu_nucleo_list = cpu_nucleo_info   
        if cpu_nucleo_list == [] and titulo_list != []:
            cpu_nucleo_list = re.findall('(?i)dual|quad', titulo_list[0])
            if cpu_nucleo_list != [] and cpu_nucleo_list[0].lower() == 'dual':
                cpu_nucleo_list = ['2']
            elif cpu_nucleo_list != [] and cpu_nucleo_list[0].lower() == 'quad':
                cpu_nucleo_list = ['4']
        
        if cpu_nucleo_list == [] and desc_cpu_list != []:
            cpu_nucleo_list = re.findall('(?i)dual|quad|\d{1,2}.core', desc_cpu_list[0])
            if cpu_nucleo_list != []:
                if cpu_nucleo_list[0].lower() == 'dual':
                    cpu_nucleo_list = ['2']
                elif cpu_nucleo_list[0].lower() == 'quad':
                    cpu_nucleo_list = ['4']
                else:
                    solo_nucleo_num = re.findall('\d+', cpu_nucleo_list[0])
                    cpu_nucleo_list = solo_nucleo_num
            elif len(desc_cpu_list) >= 2:
                cpu_nucleo_list = re.findall('(?i)dual|quad|\d{1,2}.core', desc_cpu_list[1])
                if cpu_nucleo_list != []:
                    if cpu_nucleo_list[0].lower() == 'dual':
                        cpu_nucleo_list = ['2']
                    elif cpu_nucleo_list[0].lower() == 'quad':
                        cpu_nucleo_list = ['4']
                    else:
                        solo_nucleo_num = re.findall('\d+', cpu_nucleo_list[0])
                        cpu_nucleo_list = solo_nucleo_num
        
        #----------------------------
        #DATOS_MEMORIA_RAM y DATOS_DISCO_DURO
        
        ram_cap_list = []
        disco_cap_list = []
        if titulo_list != []:
            ram_disco_info = re.findall('(?i)(\d+)\s*(gb|tb)', titulo_list[0])
            if ram_disco_info != [] :
                if len(ram_disco_info) == 2:
                    value_list = []
                    for element in ram_disco_info:
                        if element[1] == 'tb' or element[1] == 'TB':
                            value_gb = 1000*int(element[0])
                        else:
                            value_gb = int(element[0])
                        value_list.append(value_gb)
                    max_value_index = value_list.index(max(value_list))
                    disco_cap_list = [ram_disco_info[max_value_index][0] + ' ' + ram_disco_info[max_value_index][1]]
                    ram_cap_list = [str(min(value_list))]
                else:
                    text_in_parenth = re.findall('\(.*\)', titulo_list[0])
                    nuevo_titulo = titulo_list[0]
                    for text in text_in_parenth:
                        nuevo_titulo = nuevo_titulo.replace(text,'')
                    ram_disco_info = re.findall('(?i)(\d+)\s*(gb|tb)', titulo_list[0])
                    if ram_disco_info != [] and len(ram_disco_info) == 2:
                        value_list = []
                        for element in ram_disco_info:
                            if element[1] == 'tb' or element[1] == 'TB':
                                value_gb = 1000*int(element[0])
                            else:
                                value_gb = int(element[0])
                            value_list.append(value_gb)
                        max_value_index = value_list.index(max(value_list))
                        disco_cap_list = [ram_disco_info[max_value_index][0] + ' ' + ram_disco_info[max_value_index][1]]
                        ram_cap_list = [str(min(value_list))]
                    
                
                        
        ram_gen_list = []
        if ram_gen_info != []:
            ram_cap_match = re.findall('[0-9]+', ram_gen_info[0])
            ram_gen_list = re.findall('(?i)(?<=gb).*DDR.*', ram_gen_info[0])
            
            if ram_cap_list == [] and ram_cap_match != []:
                ram_cap_list = [ram_cap_match[0]]  #Se utilizan 'regular expressions - regex' para extraer el texto deseado
            
            if ram_gen_list == [] and ram_tipo_info != []:
                ram_gen_list = re.findall('.*DDR\w*', ram_tipo_info[0])
                if ram_gen_list == []:
                    ram_gen_list = [re.findall('\w+', ram_tipo_info[0])[0] + '(Verificar)']
                    
        
        disco_tipo_list = []
        if titulo_list != []:
            disco_tipo_match = re.findall(r'(?i)emmc|ssd|hdd|\brom\b', titulo_list[0])
            if disco_tipo_match == []:
                xp_compar_table = 'div[@id="comparison-table-container-6"]//td//text()'
                compar_table = response.xpath(xp_compar_table).extract()
                
                xp_storcomp_text = 'div[@id="comparison-table-container-6"]//td//*[contains(text(), "torage")]/text()'
                storcomp_text = response.xpath(xp_storcomp_text).extract_first()
                
                if storcomp_text is not None:
                    disco_info = compar_table[compar_table.index(storcomp_text) + 1]
                    disco_tipo_list = re.findall('(?i)(?<=gb).*', info_disco)
            elif len(disco_tipo_match) > 1: 
                disco_tipo_list = ['Hybrid']
            else: 
                disco_tipo_list = disco_tipo_match
                
                
                
            
        disco_match_result = []    
        if disco_info != [] and disco_cap_list == []:    
            disco_match_result = re.findall('([1-9]+)\s*(GB|TB)', disco_info[0]) #Se extrae el valor del atributo 'Hard Drive' (values_set[9])
            if disco_match_result != []:
                value = disco_match_result[0]
                if value[1] == 'TB' or value[1] == 'tb':
                    disco_gb = int(value[0])*1000
                else:
                    disco_gb = int(value[0])

                if ram_cap_list != []: 
                    if disco_gb > int(ram_cap_list[0]): 
                        disco_cap_list = [disco_match_result[0][0] + ' ' + disco_match_result[0][1]]
                    else:
                        disco_cap_list = [disco_match_result[0][0] + ' ' + disco_match_result[0][1] + '(Verificar)']
                else:
                    disco_cap_list = [disco_match_result[0][0] + ' ' + disco_match_result[0][1] + '(Verificar)']

        yield {'Laptop_Codigo': codigo_list, 
               'Laptop_Nombre': titulo_list, 
               'Laptop_Precio': precio_list, 
               'CPU_Modelo': cpu_model_list,
               'CPU_Corei_Num': corei_num_list,
               'CPU_Corei_Gen': corei_gen_list,
               'CPU_Fabricante': cpu_fab_info, 
               'CPU_Nucleos': cpu_nucleo_list,
               'CPU_Descripcion': desc_cpu_list,
               'GPU_Fabricante': gpu_fab_info,
               'GPU_Tipo': gpu_tipo_info,
               'GPU_Descripcion': desc_gpu_list,
               'Chipset_Fabricante': chipset_info,
               'RAM_Capacidad': ram_cap_list,
               'RAM_Tipo': ram_tipo_info,
               'RAM_Generacion': ram_gen_list,
               'RAM_Descripcion': desc_ram_list,
               'DiscoDuro_Capacidad': disco_cap_list,
               'DiscoDuro_Tipo': disco_tipo_list,
               'DiscoDuro_Descripcion': desc_disc_list,
               'Sistema_Operativo': sis_op_info,
               'Laptop_Marca': marca_info,
               'Laptop_Serie': serie_info,
               'Laptop_Modelo': model_info,
               'Laptop_TPantalla': pulg_info,
               'Laptop_RPantalla': resol_info,
               'Laptop_Peso': peso_info,
               'Laptop_Dimensiones': dim_info,
               'Laptop_Color': color_info,
               'Laptop_DBateria': bate_info}