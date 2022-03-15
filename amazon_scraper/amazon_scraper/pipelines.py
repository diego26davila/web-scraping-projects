# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class AmazonScraperPipeline:
    def process_item(self, item, spider):
        for k, v in item.items():
            if v == []:
                item[k] = ''
                continue
            
            if k == 'Laptop_Precio':
                item[k] = v[0].replace(',','').replace('$','').strip()
                continue
            
            item[k] = v[0].encode("ascii", "ignore").decode().strip()
            
        return item

class DuplicatesPipeline:

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['Laptop_Codigo'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.ids_seen.add(adapter['Laptop_Codigo'])
            return item
        
class AmazonScraperPipeline2:
    def process_item(self, item, spider):
        for k, v in item.items():
            if v == []:
                item[k] = ''
                continue
            
            if k == 'Laptop_Precio':
                item[k] = v[0].replace(',','').replace('S/','').strip()
                continue
            
            item[k] = v[0].encode("ascii", "ignore").decode().strip()
            
        return item
    
class DuplicatesPipeline2:

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['Laptop_SKU'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.ids_seen.add(adapter['Laptop_SKU'])
            return item