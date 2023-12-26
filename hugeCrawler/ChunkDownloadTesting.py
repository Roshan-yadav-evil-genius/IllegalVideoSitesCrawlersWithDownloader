import random
import requests
import json
from rich import print
from concurrent.futures import ThreadPoolExecutor,as_completed
import time
from threading import Thread,Event
from os import system,name
import os
import shutil


DOWNLOADED=0
start_time = time.time()
stop_event = Event()
TOTAL_SIZE=0
# Your code or statement here
with open("state.json","r") as file:
    cookie=json.loads(file.read())["cookies"]

cookies=dict()
for x in cookie:
    cookies[x['name']]=x['value']
if os.path.exists("temp"):
    shutil.rmtree("temp")

os.makedirs("temp")
print(cookies)
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

def percent(completed,total):
    x=round((completed*100)/total,3)
    return x

url="https://www.theyarehuge.com/get_file/29/1b7f5fc25ef11b1414b885b6783f2be4517c4f40cf/201000/201728/201728.mp4/"

def bytoeToMb(bytes):
    return f"{round(int(bytes)/(1024*1024),2)} Mb"


def downloadVideo(chunk_range):
    global DOWNLOADED
    myheader=headers.copy()
    start,end=chunk_range
    myheader['Range'] = f'bytes={start}-{end}'
    lresponse = requests.get(url,headers=myheader,cookies=cookies,stream=True)
    lhead=dict(lresponse.headers)
    try:
        if lhead['Content-Type'] == 'video/mp4':
            print(lhead)
            contentlength=int(lhead['Content-Length'])
            if contentlength:
                file_path=os.path.basename(url.strip("/"))
                with open(f"./temp/{file_path}_{start}_{end}.temp", 'wb') as f:
                    for chunk in lresponse.iter_content(chunk_size=4096):
                        if chunk:
                            DOWNLOADED+=len(chunk)
                            f.write(chunk)
        else:
            print("[+] Server reported the Request Loose Hand")
            time.sleep(10)
            downloadVideo(chunk_range)
    except:
        downloadVideo(chunk_range)
        


def terminalupdate():
    while not stop_event.is_set():
        execution_time = time.time()-start_time
        hours = int(execution_time // 3600)
        minutes = int((execution_time % 3600) // 60)
        seconds = int(execution_time % 60)
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        print(f"{DOWNLOADED}/{TOTAL_SIZE} => {formatted_time} => {percent(DOWNLOADED,TOTAL_SIZE)}",end="\r",flush=True)
    else:
        pass
    

response = requests.get(url,headers=headers,cookies=cookies,stream=True)
header = dict(response.headers)
TOTAL_SIZE=int(header['Content-Length'])
print(header)
print(TOTAL_SIZE/ (1024 * 1024),"MB")
total_size=TOTAL_SIZE
chunk_count = 10
chunk_size = total_size // chunk_count
chunk_ranges = [(i * chunk_size, min((i + 1) * chunk_size - 1, total_size - 1)) for i in range(chunk_count - 1)]
chunk_ranges.append((chunk_ranges[-1][1] + 1, total_size - 1))
print(chunk_ranges)
threads = []
Thread(target=terminalupdate).start()
for start, end in chunk_ranges:
    # time.sleep(random.randint(5,10))
    time.sleep(1)
    thread = Thread(target=downloadVideo, args=((start, end),))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

import glob

tempfiles=glob.glob("temp/*.temp")

tempfiles.sort(key=lambda x:int(x.split("_")[1]))

file_path=os.path.basename(url.strip("/"))
if os.path.exists(file_path):  # Check if the file exists
    print("[+] Deleted pre existing file with same name")
    os.remove(file_path)
for path in tempfiles:
    with open(file_path,"ab") as mainfile:
        with open(path,"rb") as subfile:
            mainfile.write(subfile.read())

stop_event.set()

if os.path.exists("temp"):
    shutil.rmtree("temp")
os.makedirs("temp")