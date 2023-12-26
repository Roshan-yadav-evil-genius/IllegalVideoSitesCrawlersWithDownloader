import glob
from rich import print
import shutil

tempfiles=glob.glob("temp/*.temp")

tempfiles.sort(key=lambda x:int(x.split("_")[1]))
print(tempfiles)
for path in tempfiles:
    with open("merged_output3.mp4","ab") as mainfile:
        with open(path,"rb") as subfile:
            mainfile.write(subfile.read())