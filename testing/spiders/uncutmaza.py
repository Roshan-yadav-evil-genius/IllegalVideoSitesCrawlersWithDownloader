import json
import scrapy
import random
from scrapy_playwright.page import PageMethod
from testing.items import GeneralStore
from rich import print

class UncutmazaSpider(scrapy.Spider):
    name = "uncutmaza"
    allowed_domains = ["uncutmaza.xyz"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "testing.uncutmazapipelines.uncutmazaDBPipline": 300
        }
    }

    def parse(self, response):
        videos = response.xpath("//div[@class='videos-list']/article/a")
        for video in videos:
            title = video.xpath("@title").get()
            videolink=video.xpath("@href").get()
            thumbnail = video.xpath(".//img/@data-src").get()
            data={'title':title,'thumbnail':thumbnail}
            yield scrapy.Request(videolink,
                    callback=self.parsevideourlPage,
                    cb_kwargs={'data':data})

    def parsevideourlPage(self,response,data):
        item=GeneralStore()
        videopagesrc=response.xpath("//meta[contains(@content,'.mp4')]/@content").get()
        item['title']=data['title']
        item['thumbnaillink']=data['thumbnail']
        item['videolink']=videopagesrc
        item['source']=response.url
        print(item)
        yield item
