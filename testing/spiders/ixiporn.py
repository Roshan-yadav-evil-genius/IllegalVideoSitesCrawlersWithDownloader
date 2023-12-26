from typing import Iterable
import scrapy
from scrapy.http import Request


class IxipornSpider(scrapy.Spider):
    name = "ixiporn"
    allowed_domains = ["ixiporn.cc"]
    
    def start_requests(self) :
        pass
        

    def parse(self, response):
        pass
