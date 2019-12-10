# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request
from bilicrawl.items import Bangumi, BulletHell, Score, Episode, Picture
import MySQLdb
from bilicrawl.settings import host, user, passwd, db_name


class BangumiPipeline(object):
    def __init__(self):
        self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name, charset='utf8')
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        if isinstance(item, Bangumi):
            # print('bangumis pipeline')
            sql = 'INSERT INTO bangumis (season_id, title, introduction, num, last_crawl, end) ' \
                  'VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE num = %s, last_crawl = %s, end = %s'
            try:
                self.cursor.execute(sql, (
                    item['season_id'], item['title'], item['introduction'], item['num'],
                    item['last_crawl'], item['end'], item['num'], item['last_crawl'], item['end']))
                self.db.commit()
            except Exception as e:
                print(e)
        return item


class BulletHellPipeline(object):
    def __init__(self):
        self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name, charset='utf8')
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        if isinstance(item, BulletHell):
            # print('bullet hell pipeline')
            sql = 'INSERT IGNORE INTO bullet_hells(id, moment, ts, content, poster, episode_id) ' \
                  'VALUES (%s,%s,%s,%s,%s,(SELECT id FROM episodes WHERE bangumi_id=%s AND episode=%s LIMIT 1))'
            try:
                self.cursor.execute(sql, (
                    item['id'], item['moment'], item['ts'], item['content'], item['poster'], item['bangumi_id'],
                    item['episode']))
                self.db.commit()
            except Exception as e:
                print(e)
        return item


class ScorePipeline(object):
    def __init__(self):
        self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name, charset='utf8')
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        if isinstance(item, Score):
            # print('score pipeline')
            try:
                sql = 'INSERT INTO scores (score, count, last_crawl, bangumi_id, view, follow, series_follow) ' \
                      'VALUES (%s, %s, %s, %s, %s, %s, %s) ' \
                      'ON DUPLICATE KEY UPDATE score=%s, count=%s, view=%s, follow=%s, series_follow=%s'
                self.cursor.execute(sql, (
                    item['score'], item['count'], item['last_crawl'], item['bangumi_id'], item['view'], item['follow'],
                    item['series_follow'], item['score'], item['count'], item['view'], item['follow'],
                    item['series_follow']))
                self.db.commit()
            except Exception as e:
                print(e)
        return item


class EpisodePipeline(object):
    def __init__(self):
        self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name, charset='utf8')
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        if isinstance(item, Episode):
            # print('episode pipeline')
            sql = 'INSERT INTO episodes (bangumi_id, episode, last_crawl) ' \
                  'VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE last_crawl = %s'
            try:
                self.cursor.execute(sql, (
                    item['bangumi_id'], item['episode'], item['last_crawl'], item['last_crawl']))
                self.db.commit()
            except Exception as e:
                print(e)
        return item


# 下載圖片
class DownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if isinstance(item, Picture):
            meta = {'filename': (item['file_name'] + '.jpg')}
            for image_url in item['picture_url']:
                yield Request(url=image_url, meta=meta)

    def file_path(self, request, response=None, info=None):
        return request.meta.get('filename', '')

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['picture_url'] = image_paths
        return item
