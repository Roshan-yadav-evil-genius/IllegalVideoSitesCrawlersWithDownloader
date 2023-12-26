import requests
import xml.etree.ElementTree as ET
from threading import Thread
import json
import time
import random
import pandas as pd
from rich import print
resp1 = requests.get("https://www.theyarehuge.com/sitemap/")
tree = ET.fromstring(text=resp1.content)
content=[]

def getVideos(url):
    print(url)
    resp1 = requests.get(url)
    if resp1.status_code==200:
        singlepagedata=[]
        tree = ET.fromstring(text=resp1.content)
        for index, video in enumerate(tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")):
            data=dict()
            try:
                data['title'] = video.find(".//{http://www.google.com/schemas/sitemap-video/1.1}title").text
            except:
                data['title'] =None
            try:
                data['tags']=[x.text for x in video.findall(".//{http://www.google.com/schemas/sitemap-video/1.1}tag")]
            except:
                data['tags']=None
            try:
                data['thumbnail'] = video.find(".//{http://www.google.com/schemas/sitemap-video/1.1}thumbnail_loc").text
            except:
                data['thumbnail'] = None
            try:
                data['videolink'] = video.find(".//{http://www.google.com/schemas/sitemap-video/1.1}player_loc").text
            except:
                data['videolink']=None
            try:
                data['source'] = video.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            except:
                data['source']=None
            singlepagedata.append(data)
        with open("withsource.jl", 'a') as file:
            df=pd.DataFrame(singlepagedata)
            df.to_json(file, orient='records', lines=True)

for page in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
    url=page.text
    if "type=video" in url:
        time.sleep(random.randint(1,5))
        Thread(target=getVideos,args=(url,)).start()

# with open("DirectorieCreation.json","w") as file:
#     file.write(json.dumps(content))
# file.close()
