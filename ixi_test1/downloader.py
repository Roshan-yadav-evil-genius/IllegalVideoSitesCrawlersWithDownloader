import sqlite3
from database import dbinstance
from rich import print
from rich.console import Console
import requests
from scrapy import spiderloader
from scrapy.utils import project
from os import system ,name,path,remove
from urllib.parse import urlparse, urlunparse
from threading import Thread,Event
import time
import http

system('cls' if name == 'nt' else 'clear')

print("""
                        Created By : 'Roshan yadav' https://t.me/roshanyadavse
                    
                        Powered By : 'BridgeSkillz' https://bridgeskillz.com/
                    
                                    Contact no : 8476868560
      
""")

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'identity;q=1, *;q=0',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Range': 'bytes=0-',
    'Referer': 'https://ixiporn.org/',
    'Sec-Ch-Ua': '" Not A;Brand";v="99", "Chromium";v="119", "Google Chrome";v="119"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'video',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

console = Console()
con = dbinstance.getConnection()
cur = dbinstance.getCursor()
event=Event()

currenthread=0
threads=[]
track={}


contentToDownload=[]

downloadCount = int(input("[+] Enter the no of video to Download : "))
downloadChunk = int(input("[+] Enter the no of Chunks : "))


cur.execute(f"SELECT THUMBNAILLINK, VIDEOLINK, DOWNLOADED FROM IXIPORN_SCRAPEDCONTENTS WHERE DOWNLOADED IN (2,0) ORDER BY DOWNLOADED DESC LIMIT {downloadCount}")


def showstatus():
    while not event.is_set():
        system('cls' if name == 'nt' else 'clear')
        maxKeyLength=0
        print(f"[+] Current Threads : {currenthread}")
        try:
            for key,value in track.items():
                if len(key)>maxKeyLength:
                    maxKeyLength=len(key)                    
            label=f"[+] Downloading Videos"
            spaces = " " * (maxKeyLength-len(label)+20)
            for key,value in track.items():
                label=f"[+] {key}"
                spaces = " " * (maxKeyLength-len(label)+5)
                print(label+spaces+value,flush=True)
            time.sleep(1)
        except:
            pass

def downloadImage(url,filename,status):
    if status ==2:
        try:
            remove(filename)
        except:
            pass
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
    except Exception as e:
        print(f"[+] Error : {e}")

def downloadvideo(url,filename1:str,status):
    global currenthread
    currenthread+=1
    con = sqlite3.connect("Database.sqlite")
    cur = con.cursor()
    filename=filename1.replace("%20"," ")
    try:
        if status ==2:
            try:
                remove(filename1)
                remove(filename)

            except:
                pass
        else:
            cur.execute(F"UPDATE IXIPORN_SCRAPEDCONTENTS SET DOWNLOADED=2 WHERE VIDEOLINK='{url}'")
            con.commit()
        # checkdownloaded status in db if downloaded drop request if not then request

        response = requests.get(url,headers=headers, stream=True)
        downloadedBytes=0
        if response.status_code in [200,206]:
            total_size = int(response.headers.get('Content-Length',0))
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                    downloadedBytes +=len(chunk)
                    percent=(downloadedBytes*100)/total_size
                    track[url]=f"{percent:.3f}%"
            
                cur.execute(F"UPDATE IXIPORN_SCRAPEDCONTENTS SET DOWNLOADED=1 WHERE VIDEOLINK='{url}'")
                con.commit()
        else:
            cur.execute(F"UPDATE IXIPORN_SCRAPEDCONTENTS SET DOWNLOADED=3 WHERE VIDEOLINK='{url}'")
            con.commit()
            errormsg=http.HTTPStatus(response.status_code).phrase
            error=f"Error {response.status_code} {errormsg}"
            track[url]=error
            print(error)
    except Exception as e:
        cur.execute(F"UPDATE IXIPORN_SCRAPEDCONTENTS SET DOWNLOADED=3 WHERE VIDEOLINK='{url}'")
        con.commit()
        error=f"Error {e}"
        track[url]=error
        print(error)
    try:
        track.pop(url)
    except:
        pass
    currenthread-=1
    

Thread(target=showstatus).start()



for uoimage,uovideo, status in cur.fetchall():

    upoimage=urlparse(uoimage)
    upovideo=urlparse(uovideo)

    fnoimage=path.basename(upoimage.path)
    fnovideo=path.basename(upovideo.path)

    # toimg=Thread(target=downloadImage,args=(uoimage,f"./downloads/{fnoimage}",status))
    tovid = Thread(target=downloadvideo,args=(uovideo,f"./downloads/{fnovideo}",status))

    # toimg.start()
    tovid.start()

    threads.append(tovid)


    
    while currenthread>=downloadChunk:
        time.sleep(1)

try:
    for thread in threads:
        thread.join()
    threads.clear()
except:
    pass
event.set()
print("Done")