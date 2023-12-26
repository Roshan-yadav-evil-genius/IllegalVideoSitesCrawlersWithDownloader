import scrapy
from scrapy_playwright.page import PageMethod
from testing.items import GeneralStore
from rich import print

def shouldAbortRequest(request):
    if request.resource_type in ["image","stylesheet","font"]:
        return True
    return False

class UncutjalwaSpider(scrapy.Spider):
    name = "uncutjalwa"
    allowed_domains = ["uncutjalwa.com"]
    custom_settings={
        'PLAYWRIGHT_ABORT_REQUEST':shouldAbortRequest,
        'ITEM_PIPELINES': {
            "testing.uncutjalwapipelines.uncutjalwaDBPipline": 300
        }
    }

    def parse(self, response):
        videolinks=[]
        videolist=response.xpath("//div[@class='videos-list']/article")
        for videos in videolist:
            videolink = videos.xpath("./a/@href").get()
            videoTitle = videos.xpath("./a/@title").get()
            videoThubmnail = videos.xpath(".//img/@data-src").get()
            data={'title':videoTitle,'thumbnail':videoThubmnail}
            yield scrapy.Request(
                videolink,
                callback=self.parsevideourl,
                meta={
                    "playwright": True,
                    "playwright_page_methods":[
                        PageMethod("wait_for_selector","//iframe[@data-lazy-src]")
                    ]
                    },cb_kwargs={'data':data})
        

    def parsevideourl(self,response,data):
        item= GeneralStore()
        videopagesrc=response.xpath("//iframe[@data-lazy-src]/@data-lazy-src").get()
        item['title']=data['title']
        item['thumbnaillink']=data['thumbnail']
        item['videolink']=videopagesrc
        item['source']=response.url
        print(item)
        yield item