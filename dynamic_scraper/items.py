# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class PenguinAssessmentItem(scrapy.Item):
    page_url = Field()
    category = Field()
    title = Field()
    rewarded_amount = Field()
    associated_org = Field()
    associated_loc = Field()
    about = Field()
    image_url = Field()
    dob = Field()

