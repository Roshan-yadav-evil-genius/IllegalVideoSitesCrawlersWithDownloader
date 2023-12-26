import requests
from os import system ,name
import hashlib
from threading import Thread
from rich import print

url="https://videos.trendyporn.com/videos/6/5/6/9/e/6569e4aae4a04.mp4"
track={}
def downloadvideo(url,filename):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length',0))
            downloaded=0
            print(total_size)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                    downloaded +=len(chunk)
                    percent=(downloaded*100)/total_size
                    track[url]=f"{percent:.2f}%"
                    system('cls' if name == 'nt' else 'clear')
                    print(track)

        else:
            track[url]=f"Error {response.status_code}"
    except Exception as e:
        track[url]=f"Error {e}"

downloadvideo(url,"data45.mp4")