# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class IvodlinkItem(Item):
    # define the fields for your item here like:
    # name = Field()
    id = Field()
    url = Field()
    date = Field()
    description = Field()
