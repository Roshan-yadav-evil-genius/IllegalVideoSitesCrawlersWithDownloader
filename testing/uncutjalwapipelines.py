# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


import sqlite3

class uncutjalwaDBPipline:
    def __init__(self):
        self.con = sqlite3.connect("Database.sqlite")
        self.cur = self.con.cursor()


    def process_item(self, item, spider):
        self.cur.execute("""INSERT OR IGNORE INTO UNCUTJALWA_SCRAPEDCONTENTS 
                         (ID, TITLE, THUMBNAILLINK, VIDEOLINK, SOURCE)
                         VALUES (null, ?, ?, ?, ?)""",
                         (item['title'],item['thumbnaillink'],item['videolink'],item['source']))
        self.con.commit()
        return item
