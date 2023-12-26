import json
from rich import print
import pandas as pd

urlmapping=dict()
usedurls = []
requiredvideos=[]

with open("usedvideolink.txt","r") as file:
    usedurls=file.read().split()

with open("videolinks.txt","r") as file:
    lines = [line for line in file.read().split() if line]
    for line in lines:
        value,key=line.split("__|__")
        urlmapping[key]=value

with open("final.json","r") as file:
    data = json.loads(file.read())
    for obj in data:
        if obj['videolink'] in usedurls:
            requiredvideos.append(obj)
finaloutput=[]
for video in requiredvideos:
    key = video['videolink']
    video['videolink']=urlmapping[key]
    finaloutput.append(video)

db=pd.DataFrame(finaloutput)
db.to_csv('ixiporn.csv',index=False)
