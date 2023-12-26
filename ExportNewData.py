import time
from database import dbinstance
from rich import print
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
from scrapy.utils import project
from os import path, system ,name,remove
from rich.console import Console
import pandas as pd
from CommonFunctions import getHashOf
from urllib.parse import urlparse, urlunparse
import shutil


system('cls' if name == 'nt' else 'clear')

print("""
                        Created By : 'Roshan yadav' https://t.me/roshanyadavse
                    
                        Powered By : 'BridgeSkillz' https://bridgeskillz.com/
                    
                                    Contact no : 8476868560
      
      """)

con = dbinstance.getConnection()
cur = dbinstance.getCursor()
console = Console()
TABLEMAPPING={
    "uncutmaza":"UNCUTMAZA_SCRAPEDCONTENTS",
    "uncutjalwa":"UNCUTJALWA_SCRAPEDCONTENTS"
               }

settings = project.get_project_settings()
spider_loader = SpiderLoader.from_settings(settings)
spiders = spider_loader.list()


print("[+] Available Spiders \n")


for i,spider_name in enumerate(spiders):
    spiderCls = spider_loader.load(spider_name)
    domain = getattr(spiderCls,'allowed_domains',"")
    print(f"\t {i+1}. '{spider_name.capitalize()}' for {domain[0]}")


print("\n[+] Enter the Index of Spider to Export Scraped Content :",end=" ")
spidernumber = int(input())

print("\n[+] Enter the number of Records to Export :",end=" ")
RecordCount = int(input())

SelectedSpider = spiders[spidernumber-1]

query=f"""
SELECT ID, TITLE, THUMBNAILLINK, VIDEOLINK FROM {TABLEMAPPING[SelectedSpider]} 
WHERE DOWNLOADED = 1 AND EXPORTED = FALSE LIMIT {RecordCount}
"""

def downloadedfilepathExist(filename):
    dpath=f"downloads/{filename}"
    if path.exists(dpath):
        return True
    return False

def getPath(folder,filename):
    path=f"{folder}/{filename}"

    if downloadedfilepathExist(filename):
        return path
    return None

AssestsUrls=[]

data=pd.read_sql_query(query,con)
if SelectedSpider.lower() == "uncutmaza":
    for index,row in data.iterrows():
        uoimage=row['THUMBNAILLINK']
        uovideo=row['VIDEOLINK']

        upoimage=urlparse(uoimage)
        upovideo=urlparse(uovideo)

        fnoimage=path.basename(upoimage.path)
        fnovideo=path.basename(upovideo.path)

        data.at[index,'THUMBNAILLINK']= getPath("image",fnoimage)
        data.at[index,'VIDEOLINK'] = getPath("video",fnovideo)
        try:
            shutil.move(f"./downloads/{fnoimage}",f"./Export/image/{fnoimage}")
            shutil.move(f"./downloads/{fnovideo}",f"./Export/image/{fnoimage}")
        except Exception as e:
            print(f"[+] Error : {e}")

# else:
#     for index,row in data.iterrows():
#         url=row['THUMBNAILLINK']
#         AssestsUrls.append(url)





console.print(f"\n[+] Hit Enter to Export {len(data)} Records : ",style="yellow")
input()

updateQuery=f"""
SELECT ID, TITLE, THUMBNAILLINK, VIDEOLINK FROM {TABLEMAPPING[SelectedSpider]} 
WHERE DOWNLOADED = 1 AND EXPORTED = FALSE LIMIT {RecordCount}
"""

if len(data)>0:
    try:
        currentDateTime=datetime.now()
        formatedstr = currentDateTime.strftime("%d-%m-%Y_%H:%M:%S")
        filename=f"./Export/export_{formatedstr}.csv"
        data.to_csv(filename,index=False)
        print(f"[+] Output stored in '{filename}'")

        place_holder=', '.join([f"'{url}'" for url in AssestsUrls])
        updateQuery=f"""
        UPDATE {TABLEMAPPING[SelectedSpider]} SET EXPORTED = TRUE
        WHERE THUMBNAILLINK in ({place_holder})
        """
        # print(updateQuery)
        cur.execute(updateQuery)
        con.commit()
        data.to_csv("export_latestoutput.csv",index=False)
    except Exception as e:
        print(f"[+] Error : {e}")


print("Done")