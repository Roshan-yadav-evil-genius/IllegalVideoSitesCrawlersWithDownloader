from playwright.sync_api import sync_playwright, Playwright,TimeoutError
import os
from scrapy.selector import Selector
import json
import re
from urllib.parse import urlparse
import time
# from rich import print
import json
from datetime import datetime

usedurls = []

with open("usedvideolink.txt","r") as file:
    usedurls=file.read().split()

with open("final.json" , "r") as file:
    data=json.loads(file.read())

def monitorrequest(route,request):
    pathobj = urlparse(request.url)
    filename = os.path.splitext(pathobj.path)
    if len(filename)==2 and filename[-1].startswith("."):
            extension = filename[-1]
            filename = os.path.basename(pathobj.path)
            if extension in [".png",".jpg",".svg",".webp",".gif",".woff2",".mp4",".js",".css"] or filename in ['login.php']:
                # print(f"Skipping -> {filename}")
                route.abort()
                return
            else:
                # print(f"Continue -> {filename}")
                pass

    if request.method=='POST':
        route.abort()
        return
    route.continue_()

def run(playwright: Playwright):
    firefox = playwright.firefox
    browser = firefox.launch(headless=True )
    if os.path.exists("./state.json"):
        context = browser.new_context(storage_state="state.json")
        print("Reusing state")
    else:
        context = browser.new_context()
    page = context.new_page()
    page.route("**/*",lambda route:monitorrequest(route,route.request))
    for index,video in enumerate(data):
        if video["videolink"] in usedurls or index in [9,3141]:
            continue

        videolink=None
        try:
            print(video["videolink"])
            page.goto(video["videolink"],timeout=2*60*1000)
            page.wait_for_selector("//iframe[contains(@src,'//ixiporn.cc/wp-content/')]",timeout=2*60*1000)
            text=page.frame_locator("//iframe[contains(@src,'//ixiporn.cc/wp-content/')]").locator('//video').inner_html()
            response = Selector(text=text)
            videolink = response.xpath("//source/@src").get()
            current_time = datetime.now().strftime("%H:%M:%S")

            print(f"{current_time}  {index}  '{videolink}'",flush=True)
            context.storage_state(path="state.json")
        except TimeoutError as e:
            print(f"[+] Error : {e}")
            continue

        with open("videolinks.txt",'a') as file:
            file.write(f"{videolink}__|__{video['videolink']}\n")

        with open("usedvideolink.txt","a") as file:
            file.write(f"{video['videolink']}\n")

    page.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)