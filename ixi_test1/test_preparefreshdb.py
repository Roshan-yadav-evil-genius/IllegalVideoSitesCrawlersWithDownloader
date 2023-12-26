import urllib
from database import dbinstance
import pandas as pd

con = dbinstance.getConnection()
cur = dbinstance.getCursor()



df=pd.read_csv("ixiporn.csv")

for index,item in df.iterrows():
    cur.execute("""INSERT OR IGNORE INTO IXIPORN_SCRAPEDCONTENTS 
                         (ID, TITLE, THUMBNAILLINK, VIDEOLINK)
                         VALUES (null, ?, ?, ?)""",
                         (item['title'],item['thumbnail'],item['videolink']))

    con.commit()