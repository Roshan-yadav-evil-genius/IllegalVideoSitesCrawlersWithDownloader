import time
from database import dbinstance
from rich import print
import random
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
from scrapy.utils import project
from os import system ,name
from rich.console import Console

system('cls' if name == 'nt' else 'clear')

print("""
                        Created By : 'Roshan yadav' https://t.me/roshanyadavse
                    
                        Powered By : 'BridgeSkillz' https://bridgeskillz.com/
                    
                                    Contact no : 8476868560
      
      """)


con = dbinstance.getConnection()
cur = dbinstance.getCursor()
console = Console()
STARTINGPOINT={
    "uncutmaza.xyz":"https://uncutmaza.xyz",
    "uncutjalwa.com":"https://uncutjalwa.com/main-1/"
               }

settings = project.get_project_settings()
spider_loader = SpiderLoader.from_settings(settings)
spiders = spider_loader.list()


console.print("[+] Available Spiders \n",style='yellow')

AvailableSpiders=[]

for i,spider_name in enumerate(spiders):
    spiderCls = spider_loader.load(spider_name)
    domain = getattr(spiderCls,'allowed_domains',"")
    AvailableSpiders.append((spider_name,domain[0]))
    print(f"\t {i+1}. '{spider_name.capitalize()}' for {domain[0]}")


console.print("\n[+] Enter the Index of Spider to Activate :",end=" ",style="yellow")
spidernumber = int(input())

console.print("\n[+] Enter the number of pages to scrape :",end=" ",style="yellow")
pagescount = int(input())

SelectedSpider = spiders[spidernumber-1]
console.print(f"\n[+] Selected '{SelectedSpider}' Spider for Crawling {pagescount} Pages\n",style="yellow")

SelectedSpider=AvailableSpiders[spidernumber-1]

urlsToScrape=[]

if SelectedSpider:
    cur.execute(f"SELECT URL FROM URLSTORE WHERE STATUS = FALSE AND URL LIKE '%{SelectedSpider[1]}%'")
    # urlsToScrape=random.sample([row for row in cur.fetchall()],pagescount)

urls = cur.fetchall()
if urls:
    if len(urls)<pagescount:
        console.print(f"[+] INFO currently {pagescount} pages is not available Continuing With {len(urls)}\n",style="red bold")
        urlsToScrape=urls
    else:
        urlsToScrape=random.sample([row[0] for row in urls],pagescount)
else:
    urlsToScrape = [STARTINGPOINT[SelectedSpider[1]]]
    console.print(f"[+] INFO currently {pagescount} pages is not available Continuing With  BaseUrl\n",style="red bold")

console.print(f"[+] In 5 sec Starting Crawler For {SelectedSpider[0]}\n",style="green bold")

print(urlsToScrape)
print("\n-----------------Starting Crawler-------------------\n")
time.sleep(5)

SelectedSpider = spider_loader.load(SelectedSpider[0])
settings.set('LOG_LEVEL','INFO')
process=CrawlerProcess(settings)

process.crawl(SelectedSpider,start_urls=urlsToScrape)

process.start()