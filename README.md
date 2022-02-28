# WEB-SCRAPING LAS LAPTOPS DE AMAZON

## Requerimientos

- Python3 (y *pip* package mager) 
- Scrapy Framework: Para instalarlo, ejecutar en la terminal (cmd, PowerShell, etc.) el siguiente comando:
    ```
    pip install Scrapy
    ```
- Proxy API: Para evitar el bloqueo de Amazon, crear una cuenta en un servicio de API (Scraper API en el ejemplo: www.scraper.com) y obtener la clave del API de la cuenta (API_KEY).

## Instrucciones

1. Abrir la linea de comandos (cmd, powershell u otro)
2. Clonar el repositorio de GitHub con el siguiente comando:
    ```
    git clone https://github.com/diego26davila/web-scraping-projects.git
    ```
3. Ir al directorio del projecto 
    ```
    cd amazon-scraper
    ```
4. Crear archivo CSV con los datos de las laptops extraidas de las paginas de Amazon
    ```
    scrapy crawl amazon -o <nombre>.csv
    ```