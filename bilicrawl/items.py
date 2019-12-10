# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Bangumi(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    season_id = scrapy.Field()
    title = scrapy.Field()
    introduction = scrapy.Field()
    num = scrapy.Field()
    last_crawl = scrapy.Field()
    end = scrapy.Field()


class BulletHell(scrapy.Item):
    id = scrapy.Field()
    moment = scrapy.Field()
    ts = scrapy.Field()
    content = scrapy.Field()
    poster = scrapy.Field()
    bangumi_id = scrapy.Field()
    episode = scrapy.Field()


class Score(scrapy.Item):
    score = scrapy.Field()
    count = scrapy.Field()
    last_crawl = scrapy.Field()
    bangumi_id = scrapy.Field()
    view = scrapy.Field()
    follow = scrapy.Field()
    series_follow = scrapy.Field()


class Episode(scrapy.Item):
    bangumi_id = scrapy.Field()
    episode = scrapy.Field()
    last_crawl = scrapy.Field()


class Picture(scrapy.Item):
    picture_url = scrapy.Field()
    file_name = scrapy.Field()
