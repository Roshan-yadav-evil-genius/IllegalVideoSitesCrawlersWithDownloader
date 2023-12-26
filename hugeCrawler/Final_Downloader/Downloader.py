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
uploadStatus=dict()

# Get the current date and time

start_time = time.time()
stop_event = Event()
UPLOADSTATUS=dict()
ERROR=dict()
CURRENTHREAD=0
finalOutputUrl=False

# Fill Required Information
HOSTNAME = "sg.storage.bunnycdn.com"
USERNAME = "onlyhd"
PASSWORD = "9da4206d-b81e-4b78-bd477a9c1466-47c1-46a0"

def logError(msg:str):
    formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if msg in ERROR:
        ERROR[msg]+=1
    else:
        ERROR[msg]=1
    with open("log.log" , "a") as file:
        file.write(f" {formatted_datetime} [+] Log : {msg}")

ftp_server = FTP(HOSTNAME, USERNAME, PASSWORD,encoding="utf-8")

def createdir(ftp:FTP,url:str)->str:
    dir = url.rstrip('/').split('/')[-3:]
    try:
        ftp.cwd("/onlyhd/theyarehuge")
    except Exception as e:
        print(f"[+] Navigation Error : {e}")
    try:
        ftp.mkd(dir[0])
        print(f"[+] Created : {dir[0]}")
    except Exception as e:
        print(f"[+] Main Error : {e}")
    try:
        ftp.cwd(dir[0])
    except Exception as e:
        print(f"[+] Navigation Error : {e}")
    try:
        ftp.mkd(dir[1])
        print(f"[+] Created : {dir[1]}")
    except Exception as e:
        print(f"[+] Sub Error : {e}")
    
    return f"/onlyhd/theyarehuge/{dir[0]}/{dir[1]}/{dir[2]}"

with open("state.json","r") as file:
    cookies={x['name']:x['value'] for x in json.loads(file.read())["cookies"]}

if os.path.exists("temp"):
    shutil.rmtree("temp")
os.makedirs("temp")

if not os.path.exists("downloads"):
    os.makedirs("downloads")

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

FetchedLengthStore=dict()
TotalLengthStore=dict()


def upload_progress(filename,data):
    uploadStatus[f"{filename}_u"] += len(data)
    try:
        percent = (uploadStatus[f"{filename}_u"]/uploadStatus[f"{filename}_t"]) * 100
        UPLOADSTATUS[filename]= f"{percent:.2f}%"
    except Exception as e:
        logError(f"upload_progress({filename},data)->{e}")
        print(f"[+] Error : {e}")

def uploadToFtp(ftp_server:FTP,filename,url):
    global total
    try:
        with open(f"./downloads/{filename}","rb") as rdata:
            uploadStatus[f"{filename}_t"]=os.path.getsize(f"./downloads/{filename}")
            uploadStatus[f"{filename}_u"]=0
            ftp_server.storbinary(f'STOR {createdir(ftp_server,url)}', rdata,callback=lambda data: upload_progress(filename,data))
        os.remove(f"./downloads/{filename}")
    except Exception as e:
        logError(f"uploadToFtp({filename},{url})->{e}")



def downloadChunk(url,filename,start_index, end_index,attempt=1):
    if attempt ==3:
        return

    chunkHeader = headers.copy()
    chunkHeader['Range'] = f'bytes={start_index}-{end_index}'
    try:
        chunkresp = requests.get(url,headers=chunkHeader,cookies=cookies,stream=True)
        chunkContentType = chunkresp.headers.get("Content-Type")
        if chunkContentType == "video/mp4":
            with open(f"./temp/{filename}_{start_index}_{end_index}.temp","wb") as file:
                for chunk in chunkresp.iter_content(chunk_size=1024):
                    file.write(chunk)

                    if filename in FetchedLengthStore:
                        FetchedLengthStore[fileName]+=len(chunk)
                    else:
                        FetchedLengthStore[filename]=len(chunk)
        else:
            raise ValueError(f"Unsupported Content Type : {chunkContentType} Require video/mp4 type")
    except Exception as e:
        print(f"[+] Error downloadChunk() : {e}")
        logError(f"downloadChunk({filename},{start_index},{end_index},{attempt})->{e}")
        time.sleep(10*attempt)
        attempt+=1
        downloadChunk(url,filename,start_index, end_index,attempt)


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
            TotalLengthStore[filename]=ContentLength

            chunk_count = 10
            chunk_size = ContentLength // chunk_count
            chunk_ranges = [(i * chunk_size, min((i + 1) * chunk_size - 1, ContentLength - 1)) for i in range(chunk_count - 1)]
            chunk_ranges.append((chunk_ranges[-1][1] + 1, ContentLength - 1))

            threads=[]
            for start, end in chunk_ranges: 
                time.sleep(random.randint(1,10))
                thread = Thread(target=downloadChunk, args=(url,filename,start, end,))
                thread.start()
                threads.append(thread)
            
            for th in threads:
                th.join()
            import glob
            tempfiles = glob.glob(f"./temp/{filename}_*.temp")
            tempfiles.sort(key=lambda x:int(x.split("_")[1]))

            with open(f"./downloads/{filename}","wb") as mainfile:
                for path in tempfiles:
                    with open(path,"rb") as subfile:
                        mainfile.write(subfile.read())
                    os.remove(path)
            


            # uploadToFtp(ftp_server,filename,url)

            # Thread(target=uploadToFtp,args=(ftp_server,filename,url)).start()


            CURRENTHREAD-=1
        else:
            raise ValueError(f"Unsupported Content Type : {ContentType} Require video/mp4 type")
    except Exception as e:
        print(f"[+] Error DownloadVideo() : {e}")
        logError(f"DownloadVideo({url},{filename},{attempt})->{e}")

        time.sleep(10*attempt)
        attempt+=1
        DownloadVideo(url,filename,attempt)

def percent(completed,total):
    x=round((completed*100)/total,3)
    return x

def ShowStatusInTerminal():
    while not stop_event.is_set():
        system('cls' if name == 'nt' else 'clear')
        execution_time = time.time()-start_time
        hours = int(execution_time // 3600)
        minutes = int((execution_time % 3600) // 60)
        seconds = int(execution_time % 60)
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        newdict=dict()
        for key,value in TotalLengthStore.items():
            if key in FetchedLengthStore:
                fetched=FetchedLengthStore[key]
                newdict[key]=percent(fetched,value)

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