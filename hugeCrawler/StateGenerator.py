from playwright.sync_api import sync_playwright, Playwright,TimeoutError
import os
from scrapy.selector import Selector
import json
import re
from rich import print
from urllib.parse import urlparse
import time
# from rich import print
import json
from datetime import datetime

usedurls =False
catchedurl=[]
def monitorrequest(route,request):
    global usedurls
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
                    usedurls=request.url
                route.abort()
                return
            else:
                print(f"Loading -> {request.url}")
                pass
    if request.method=='POST':
        route.abort()
        return
    route.continue_()




playwright = sync_playwright().start()
browser = playwright.firefox.launch(headless=True )
context = browser.new_context(storage_state="state.json")
page = context.new_page()
page.route("**/*",lambda route:monitorrequest(route,route.request))
page.goto("https://www.theyarehuge.com/embed/201728")
while not usedurls:
        page.wait_for_timeout(1000)
        print("wait")
print("Done")
context.storage_state(path="state.json")
page.close()
browser.close()

print(usedurls)