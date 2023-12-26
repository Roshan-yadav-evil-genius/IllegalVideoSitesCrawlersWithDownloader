from playwright.sync_api import sync_playwright, Playwright,TimeoutError
import os
from scrapy.selector import Selector
import json
import re
from urllib.parse import urlparse
import time
from rich import print
import json
from datetime import datetime

usedurls = []

with open("usedvideolink.txt","r") as file:
    usedurls=file.read().split()

with open("Embedoutput.json" , "r") as file:
    data=json.loads(file.read())

finalOutputUrl=False

def monitorrequest(route,request):
    global finalOutputUrl
    pathobj = urlparse(request.url.strip("/"))
    filename = os.path.splitext(pathobj.path)
    if str(filename[0]).endswith("/") and not filename[-1]:
         pathobj = urlparse(str(filename[0]).strip("/"))
         filename = os.path.splitext(pathobj.path)
    # print(filename)
    if len(filename)==2 and filename[-1].startswith("."):
            extension = filename[-1]
            filename = os.path.basename(request.url)
            if extension in [".png",".jpg",".svg",".webp",".gif",".woff2",".mp4",".php",".css"]:
                if extension ==".mp4":
                    print(f"Found -> {request.url}")
                    finalOutputUrl=request.url
                route.abort()
                return
            else:
                print(f"Loading -> {request.url}")
                pass
    if request.method=='POST':
        route.abort()
        return
    route.continue_()

def run(playwright: Playwright):
    global finalOutputUrl
    firefox = playwright.firefox
    browser = firefox.launch(headless=True )
    context = browser.new_context(storage_state="state.json")
    page = context.new_page()
    page.route("**/*",lambda route:monitorrequest(route,route.request))
    for index,video in enumerate(data):
        if video["videolink"] in usedurls or not video["videolink"] :
            print(f"[+] Skipping : {index}")
            continue

        page.goto(video["videolink"])
        maxWaitTime = 0
        while not finalOutputUrl and maxWaitTime<20:
            page.wait_for_timeout(1000)
            maxWaitTime+=1
            print("wait")
        if finalOutputUrl:
            print(f"[+] Done {index}")
            with open("videolinks.txt",'a') as file:
                file.write(f"{finalOutputUrl}__|__{video['videolink']}\n")

            with open("usedvideolink.txt","a") as file:
                file.write(f"{video['videolink']}\n")

        finalOutputUrl=False

    page.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)