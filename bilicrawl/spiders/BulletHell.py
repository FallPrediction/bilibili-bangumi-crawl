# -*- coding: utf-8 -*-
import scrapy
import re
import json
from bilicrawl.items import Bangumi, BulletHell, Score, Episode, Picture
from bilicrawl.settings import host, user, passwd, db_name
import datetime
import MySQLdb


class BullethellSpider(scrapy.Spider):
    name = 'Bangumi'
    # allowed_domains = ['www.bilibili.com']
    start_urls = [
        'https://api.bilibili.com/pgc/season/index/result?season_version=-1&area=-1&is_finish=0&copyright=-1&season_status=-1&season_month=-1&year=-1&style_id=-1&order=3&st=1&sort=0&page=1&season_type=1&pagesize=20&type=1']
    season_set = set()

    # 取得資料庫所有需要抓取的番id
    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name, charset='utf8')
    cursor = db.cursor()
    sql = 'SELECT * FROM bangumis WHERE end >=(NOW() - INTERVAL 1 MONTH) OR end IS NULL'
    cursor.execute(sql)
    result = cursor.fetchall()
    for row in result:
        season_set.add(row[0])
    db.close()

    # 加入目前連載中的番id
    def parse(self, response):
        result = json.loads(response.text)
        try:
            for l in result['data']['list']:
                self.season_set.add(l['season_id'])
            if result['data']['has_next']:
                yield scrapy.Request(url=(
                        'https://api.bilibili.com/pgc/season/index/result?season_version=-1&area=-1&is_finish=0&copyright=-1&season_status=-1&season_month=-1&year=-1&style_id=-1&order=3&st=1&sort=0&page=' + str(
                    result['data']['num'] + 1) + '&season_type=1&pagesize=20&type=1'), callback=self.parse)
        except KeyError:
            print('seaon_id查詢錯誤')
        except Exception as e:
            print(e)

        # 開始抓取番
        for seaon_id in self.season_set:
            yield scrapy.Request(url=('https://www.bilibili.com/bangumi/play/ss' + str(seaon_id) + '/'),
                                 callback=self.parse_bangumi)

    def parse_bangumi(self, response):
        # bangumi item
        bangumi = Bangumi()
        season_id = response.request.url.split('/')[-2].replace('ss', '')
        bangumi['season_id'] = season_id

        bangumi['last_crawl'] = datetime.datetime.today()
        title = response.css('.media-right>a::text').get().strip()
        bangumi['title'] = title
        bangumi['introduction'] = response.css('.media-desc span::text').get().strip()
        if '完结' in response.css('.pub-wrapper span::text').get():
            end = True
            bangumi['end'] = datetime.datetime.today()
            bangumi_result = json.loads(
                re.search(r'"epList":\[(.*?)"\}\]', response.text).group().replace('"epList":', ''))
            bangumi['num'] = bangumi_result[-1]['i'] + 1
        else:
            end = False
            bangumi['end'] = None
            bangumi['num'] = None
        yield bangumi

        # picture item
        picture = Picture()
        picture['file_name'] = season_id
        picture['picture_url'] = [re.search(r'og:image" content="(.*?)">', response.text).group().replace(
            'og:image" content="', '').replace('">', '')]
        yield picture

        # score item
        score_result = json.loads(re.search(r'"rating"(.*?)\}', response.text).group().replace('"rating":', ''))
        sscore = score_result['score']
        count = score_result['count']

        yield scrapy.Request(
            url=('https://api.bilibili.com/pgc/web/season/stat?season_id=' + season_id),
            callback=self.parse_score_data, meta={'season_id': season_id, 'sscore': sscore, 'count': count})

        # bullet hell item and episode
        if end:
            for r in bangumi_result:
                yield scrapy.Request(url=('https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(r['cid'])),
                                     callback=self.parse_bullet_hell,
                                     meta={'season_id': season_id, 'episode': r['i'] + 1})

    # 取得追番、系列追番、觀看次數
    def parse_score_data(self, response):
        score = Score()
        result = json.loads(response.text)
        score['score'] = response.meta['sscore']
        score['count'] = response.meta['count']
        score['last_crawl'] = datetime.datetime.today()
        score['bangumi_id'] = response.meta['season_id']
        score['view'] = result['result']['views']
        score['follow'] = result['result']['follow']
        score['series_follow'] = result['result']['series_follow']
        yield score

    # 取得彈幕、紀錄抓取時間戳
    def parse_bullet_hell(self, response):
        season_id = response.meta['season_id']
        eepisode = response.meta['episode']

        db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name, charset='utf8')
        cursor = db.cursor()
        sql = 'SELECT id, last_crawl FROM episodes WHERE bangumi_id = %s AND episode = %s'
        cursor.execute(sql, (season_id, eepisode))
        result = cursor.fetchone()
        if result:
            last_crawl = datetime.datetime.timestamp(result[1])
        else:
            last_crawl = 0

        # episode item
        episode = Episode()
        episode['bangumi_id'] = season_id
        episode['episode'] = eepisode
        episode['last_crawl'] = datetime.datetime.now()
        yield episode

        bullet_hells = response.css('d')
        for b in bullet_hells:
            p = b.css(':scope::attr(p)').get().split(',')
            if float(p[4]) > last_crawl:
                # bullet item
                bullet = BulletHell()
                bullet['id'] = p[7]
                bullet['moment'] = p[0]
                bullet['ts'] = datetime.datetime.fromtimestamp(float(p[4]))
                bullet['content'] = b.css(':scope::text').get()
                bullet['poster'] = p[6]
                bullet['bangumi_id'] = season_id
                bullet['episode'] = eepisode
                yield bullet
