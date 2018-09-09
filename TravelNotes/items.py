# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TravelNotesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    iid = scrapy.Field()

    title = scrapy.Field()

    author = scrapy.Field()

    shareTime = scrapy.Field()

    viewCount = scrapy.Field()

    commentCount = scrapy.Field()

    favCount = scrapy.Field()

    shareCount = scrapy.Field()

    startTime = scrapy.Field()

    duration = scrapy.Field()

    personType = scrapy.Field()

    averageCost = scrapy.Field()

    content = scrapy.Field()
