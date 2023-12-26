import glob
from rich import print
import os

filename="201728.mp4"
tempfiles = glob.glob(f"./temp/{filename}_*.temp")
tempfiles.sort(key=lambda x:int(x.split("_")[1]))

with open(filename,"wb") as mainfile:
    for path in tempfiles:
        with open(path,"rb") as subfile:
            mainfile.write(subfile.read())
        os.remove(path)