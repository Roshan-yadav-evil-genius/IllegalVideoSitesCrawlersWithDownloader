import ftplib
import pandas as pd
from rich import print
from ftplib import FTP
# Fill Required Information
HOSTNAME = "sg.storage.bunnycdn.com"
USERNAME = "onlyhd"
PASSWORD = "9da4206d-b81e-4b78-bd477a9c1466-47c1-46a0"

ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD,encoding="utf-8")

createddir=[]
for index,row in pd.read_json("output_file.jl",lines=True).iterrows():
    print(index)
    try:
        url=row['dummylink']
        dir = url.rstrip('/').split('/')[-3:-1]
        if (dir[0] in createddir) and  ( dir[1] in createddir):
            print(f"[+]Skipping....{dir[0]}/{dir[1]}")
            continue
    except:
        continue

    try:
        ftp_server.cwd("/onlyhd/theyarehuge")
    except Exception as e:
        print(f"[+] Navigation Error : {e}")
    try:
        ftp_server.mkd(dir[0])
        print(f"[+] Created : {dir[0]}")
    except Exception as e:
        createddir.append(dir[0])
        print(f"[+] Main Error : {e}")
    try:
        ftp_server.cwd(dir[0])
    except Exception as e:
        print(f"[+] Navigation Error : {e}")
    try:
        ftp_server.mkd(dir[1])
        print(f"[+] Created : {dir[1]}")
    except Exception as e:
        createddir.append(dir[1])
        print(f"[+] Sub Error : {e}")

def createdir(ftp:FTP,url:str)->str:
    dir = url.rstrip('/').split('/')[-3:]
    if (dir[0] in createddir) and  ( dir[1] in createddir):
        print(f"[+]Skipping....{dir[0]}/{dir[1]}")
        return
    try:
        ftp.cwd("/onlyhd/theyarehuge")
    except Exception as e:
        print(f"[+] Navigation Error : {e}")
    try:
        ftp.mkd(dir[0])
        print(f"[+] Created : {dir[0]}")
    except Exception as e:
        createddir.append(dir[0])
        print(f"[+] Main Error : {e}")
    try:
        ftp.cwd(dir[0])
    except Exception as e:
        print(f"[+] Navigation Error : {e}")
    try:
        ftp.mkd(dir[1])
        print(f"[+] Created : {dir[1]}")
    except Exception as e:
        createddir.append(dir[1])
        print(f"[+] Sub Error : {e}")
    
    return f"/onlyhd/theyarehuge/{dir[0]}/{dir[1]}/{dir[2]}"