import json
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright
import os
from ftplib import FTP
import pandas as pd
from os import system,name
import requests
from threading import Thread,Event
import time
import random
import shutil
from rich import print
from datetime import datetime
import os
# Get the current date and time

start_time = time.time()
stop_event = Event()
UPLOADSTATUS=dict()
ERROR=dict()
CURRENTHREAD=0
finalOutputUrl=False

def logError(msg:str):
    formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if msg in ERROR:
        ERROR[msg]+=1
    else:
        ERROR[msg]=1
    with open("log.log" , "a") as file:
        file.write(f" {formatted_datetime} [+] Log : {msg}")


with open("state.json","r") as file:
    cookies={x['name']:x['value'] for x in json.loads(file.read())["cookies"]}


headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'identity;q=1, *;q=0',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Range': 'bytes=0-',
    'Referer': 'https://www.theyarehuge.com/',
    'Sec-Ch-Ua': '" Not A;Brand";v="99", "Chromium";v="119", "Google Chrome";v="119"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'video',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}


def download_with_fdm(url):
    try:
        parsed_url = urlparse(url)
        url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}".strip("/")
        fdm_path = '/opt/freedownloadmanager/fdm'
        command = f'"{fdm_path}" {url}'
        os.system(command)
        print(f"Sent MP4 link to Free Download Manager: {url}")
    except Exception as e:
        print(f"Error sending MP4 link to Free Download Manager: {e}")

def wait_based_on_content_size(content_length):
    if content_length < 100 * 1024 * 1024:  # Size less than 100MB (converted to bytes)
        time.sleep(30)
    elif 100 * 1024 * 1024 < content_length < 400 * 1024 * 1024:  # Size between 100MB and 400MB
        time.sleep(60)
    else:  # Size greater than 400MB
        time.sleep(120)

def DownloadVideo(url,filename,attempt=1):
    global CURRENTHREAD

    if attempt==3:
        CURRENTHREAD-=1
        return
    
    CURRENTHREAD+=1
    try:
        response = requests.get(url,headers=headers,cookies=cookies,stream=True)
        ContentType = response.headers.get("Content-Type")

        if ContentType == "video/mp4":
            print("Downloading")
            ContentLength = int(response.headers.get("Content-Length"))

            download_with_fdm(url)

            wait_based_on_content_size(ContentLength)

            CURRENTHREAD-=1
        else:
            raise ValueError(f"Unsupported Content Type : {ContentType} Require video/mp4 type")
    except Exception as e:
        print(f"[+] Error DownloadVideo() : {e}")
        logError(f"DownloadVideo({url},{filename},{attempt})->{e}")

        time.sleep(10*attempt)
        attempt+=1
        DownloadVideo(url,filename,attempt)



def ShowStatusInTerminal():
    while not stop_event.is_set():
        system('cls' if name == 'nt' else 'clear')
        execution_time = time.time()-start_time
        hours = int(execution_time // 3600)
        minutes = int((execution_time % 3600) // 60)
        seconds = int(execution_time % 60)
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        newdict=dict()

        print(f"[+] Uptime : {formatted_time}")
        print(ERROR)
        print(newdict)
        print(UPLOADSTATUS)
        time.sleep(1)


Thread(target=ShowStatusInTerminal).start()

threads=[]


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

playwright = sync_playwright().start()
browser = playwright.firefox.launch(headless=True )
context = browser.new_context(storage_state="state.json")
page = context.new_page()
page.route("**/*",lambda route:monitorrequest(route,route.request))


usedurls = []

with open("usedvideolink.txt","r") as file:
    usedurls=file.read().split()
data=pd.read_json("output_file.jl",lines=True)

for index,video in data.iterrows():
    if video["videolink"] in usedurls:
        print(f"[+] Skipping {index}")
        continue

    page.goto(video["videolink"])
    maxWaitTime = 0
    while not finalOutputUrl and maxWaitTime<20:
        page.wait_for_timeout(1000)
        maxWaitTime+=1
        print("wait")
    
    if not finalOutputUrl:
        continue

    parsed_url = urlparse(finalOutputUrl)

    url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}".strip("/")
    print(url)
    fileName=os.path.basename(parsed_url.path.strip("/"))

    # th=Thread(target=DownloadVideo,args=(url,fileName))
    # th.start()
    # threads.append(th)

    DownloadVideo(url,fileName)

    with open("usedvideolink.txt","a") as file:
        file.write(f'{video["videolink"]}\n')
    # time.sleep(random.randint(10,20))

    finalOutputUrl=False
    # while CURRENTHREAD>=5:
    #     time.sleep(1)

page.close()
browser.close()
for th in threads:
    th.join()

stop_event.set()