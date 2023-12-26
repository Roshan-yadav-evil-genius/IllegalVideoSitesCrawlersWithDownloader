# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import sqlite3
from scrapy import signals
from rich import print
# useful for handling different item types with a single interface
# from itemadapter import is_item, ItemAdapter


class TestingSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class TestingDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        self.con = sqlite3.connect("Database.sqlite")
        self.cur = self.con.cursor()
        self.create_table()
    
    def create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS URLSTORE (
                ID INTEGER PRIMARY KEY,
                URL TEXT UNIQUE,
                STATUS BOOLEAN DEFAULT FALSE
            ); """)
        
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS CRAWLER_LIFECYCLE (
                ID INTEGER PRIMARY KEY,
                FROMURL TEXT NULL,
                URL TEXT NULL,
                UNIQUE(FROMURL, URL)
                FOREIGN KEY (FROMURL) REFERENCES URLSTORE(ID),
                FOREIGN KEY (URL) REFERENCES URLSTORE(ID)
            ); """)
        
        self.con.commit()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        self.cur.execute("""SELECT ID, STATUS FROM URLSTORE WHERE URL = ?""",(request.url,))
        presence = self.cur.fetchone()
        if presence is None:
            self.cur.execute("""INSERT OR IGNORE INTO URLSTORE (URL) VALUES (?)""",(request.url,))
            self.con.commit()
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        extractedfrom = response.url

        self.cur.execute("""UPDATE URLSTORE SET STATUS = ? WHERE URL = ?""",(True,extractedfrom,))

        links=[]
        links = response.xpath("//a[contains(@href,'/category/') or contains(@href,'/page/') or contains(@href,'/tag/') ]/@href").getall()

        links=[(link,) for link in links]
        self.cur.executemany("""INSERT OR IGNORE INTO URLSTORE (URL) VALUES (?)""",links)
        self.con.commit()

        self.cur.execute("""SELECT ID, STATUS FROM URLSTORE WHERE URL = ?""",(extractedfrom,))
        fromurlid = self.cur.fetchone()[0]

        mapping=[]
        place_holder=', '.join([f"'{url[0]}'" for url in links])
        
        self.cur.execute(f"""SELECT ID FROM URLSTORE WHERE URL IN ({place_holder})""")
        mapping=[(fromurlid,urlinfo[0]) for urlinfo in self.cur.fetchall()]

        self.cur.executemany("""INSERT OR IGNORE INTO CRAWLER_LIFECYCLE (FROMURL,URL) VALUES (?, ?)""",mapping)

        self.con.commit()

            
            # print(links)
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
