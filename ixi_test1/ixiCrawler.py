from playwright.sync_api import sync_playwright, Playwright
import os
from scrapy.selector import Selector
import json
import re
import time
import random

count=0
urls=['https://ixiporn.cc/']

usedurls = []

with open("usedurl.txt","r") as file:
    usedurls=file.read().split()

for x in range(2,1759):
    url=f'https://ixiporn.cc/page/{x}'
    urls.append(url)

def extractResponse(rawhtml):
    videos=[]
    pagination=[]
    response = Selector(text=rawhtml)
    for video in response.xpath("//div[@data-post-id]"):
        thumbnail = video.xpath(".//img[@data-src]/@data-src").get()
        videolink = video.xpath(".//a[@href]/@href").get()
        title = video.xpath(".//span[@class='title']/text()").get()
        data = " ".join([x.strip() for x in title.split()])
        with open("output.jl","a") as file:
            data=json.dumps({"title":data,"thumbnail":thumbnail,"videolink":videolink})
            file.write(f"{data}\n")




def run(playwright: Playwright):
    firefox = playwright.firefox
    browser = firefox.launch(headless=True)
    if os.path.exists("./state.json"):
        context = browser.new_context(storage_state="state.json")
        print("Reusing state")
    else:
        context = browser.new_context()
    page = context.new_page()
    page.route(re.compile(r"\.(jpg|jpeg|png|svg)$"), 
    lambda route: route.abort()) 
    for url in urls:
        if url in usedurls:
            print("Skipping...")
            continue
        page.goto(url)
        page.wait_for_selector("//div[@data-post-id]",timeout= 5*60*1000)
        extractResponse(page.content())
        with open("usedurl.txt","a") as file:
            file.write(f"{url}\n")
        # waittime=random.randint(4,60)
        # time.sleep(waittime)
    page.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)