# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class LinkshellItem(Item):
    name = Field()
    world = Field()
    lodestone_id = Field()
    type_string = Field()

class CharacterItem(Item):
    name = Field()
    world = Field()
    lodestone_id = Field()
    avatar_url = Field()
    ls_lodestone_id = Field()
    cwls_lodestone_id = Field()
    is_owner = Field()
