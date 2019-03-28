# -*- coding: utf-8 -*-

<<<<<<< HEAD
# Define here the models1 for your scraped items
=======
# Define here the models for your scraped items
>>>>>>> f38684dd49bf46158a1ee1bc4f10185034cc3b32
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    salary = scrapy.Field()
    experience = scrapy.Field()
    diploma = scrapy.Field()
    amount = scrapy.Field()
    career = scrapy.Field()
    address = scrapy.Field()
    position = scrapy.Field()
    category = scrapy.Field()
    trial_time = scrapy.Field()
    sex = scrapy.Field()
    age = scrapy.Field()
    description = scrapy.Field()
    benefits = scrapy.Field()
    require_skill = scrapy.Field()
    contact = scrapy.Field()
    expired = scrapy.Field()
    created = scrapy.Field()
