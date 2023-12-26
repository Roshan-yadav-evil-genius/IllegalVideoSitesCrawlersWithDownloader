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
from CommonFunctions import getHashOf
import time
import http

system('cls' if name == 'nt' else 'clear')

print("""
                        Created By : 'Roshan yadav' https://t.me/roshanyadavse
                    
                        Powered By : 'BridgeSkillz' https://bridgeskillz.com/
                    
                                    Contact no : 8476868560
      
      """)


console = Console()
con = dbinstance.getConnection()
cur = dbinstance.getCursor()
event=Event()

settings = project.get_project_settings()
spider_loader = spiderloader.SpiderLoader.from_settings(settings)
spiders = spider_loader.list()

threads=[]
track={}


contentToDownload=[]

downloadCount = int(input("[+] Enter the no of video to Download : "))
downloadChunk = int(input("[+] Enter the no of Chunks : "))
chunkDownloadInterval =int(input("[+] Enter the interval in seconds between Chunks : "))


cur.execute(f"SELECT THUMBNAILLINK, VIDEOLINK, DOWNLOADED FROM UNCUTMAZA_SCRAPEDCONTENTS WHERE DOWNLOADED IN (2,0) AND SOURCE LIKE '%uncutmaza.xyz%' ORDER BY DOWNLOADED DESC LIMIT {downloadCount}")


def showstatus():
    while not event.is_set():
        system('cls' if name == 'nt' else 'clear')
        maxKeyLength=0
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

def downloadImage(url,filename):
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
    except Exception as e:
        print(f"[+] Error : {e}")

def downloadvideo(url,filename,status):
    con = sqlite3.connect("Database.sqlite")
    cur = con.cursor()
    try:
        if status ==2:
            try:
                remove(filename)
            except:
                pass
        else:
            cur.execute(F"UPDATE UNCUTMAZA_SCRAPEDCONTENTS SET DOWNLOADED=2 WHERE VIDEOLINK='{url}'")
            con.commit()
        # checkdownloaded status in db if downloaded drop request if not then request

        response = requests.get(url, stream=True)
        downloadedBytes=0
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length',0))
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                    downloadedBytes +=len(chunk)
                    percent=(downloadedBytes*100)/total_size
                    track[url]=f"{percent:.3f}%"
            
                cur.execute(F"UPDATE UNCUTMAZA_SCRAPEDCONTENTS SET DOWNLOADED=1 WHERE VIDEOLINK='{url}'")
                con.commit()
        else:
            cur.execute(F"UPDATE UNCUTMAZA_SCRAPEDCONTENTS SET DOWNLOADED=3 WHERE VIDEOLINK='{url}'")
            con.commit()
            errormsg=http.HTTPStatus(response.status_code).phrase
            error=f"Error {response.status_code} {errormsg}"
            track[url]=error
            print(error)
    except Exception as e:
        cur.execute(F"UPDATE UNCUTMAZA_SCRAPEDCONTENTS SET DOWNLOADED=3 WHERE VIDEOLINK='{url}'")
        con.commit()
        error=f"Error {e}"
        track[url]=error
        print(error)
    

Thread(target=showstatus).start()



for uoimage,uovideo, status in cur.fetchall():

    upoimage=urlparse(uoimage)
    upovideo=urlparse(uovideo)

    fnoimage=path.basename(upoimage.path)
    fnovideo=path.basename(upovideo.path)

    toimg=Thread(target=downloadImage,args=(uoimage,f"./downloads/{fnoimage}"))
    tovid = Thread(target=downloadvideo,args=(uovideo,f"./downloads/{fnovideo}",status))

    toimg.start()
    tovid.start()

    threads.append((toimg,tovid))
    
    if len(threads)==downloadChunk:
        for img_thread,vide_thread in threads:
            img_thread.join()
            vide_thread.join()
        threads.clear()
        time.sleep(chunkDownloadInterval)

for thread in threads:
    thread.join()
threads.clear()
event.set()
print("Done")