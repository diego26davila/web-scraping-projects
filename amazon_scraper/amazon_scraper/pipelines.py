# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class AmazonScraperPipeline:
    def process_item(self, item, spider):
        for k, v in item.items():
            if not v:
                item[k] = ''
                continue
            
            if k == 'Laptop_Precio':
                item[k] = [i.replace(',','').replace('$','') for i in v]
                continue
            
            item[k] = [i.encode("ascii", "ignore").decode().strip() for i in v]
            
        return item
