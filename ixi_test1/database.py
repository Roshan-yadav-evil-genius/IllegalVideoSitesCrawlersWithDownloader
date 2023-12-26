import sqlite3
import os

class DBInstance(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(DBInstance, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        self.con = sqlite3.connect("Database.sqlite")
        self.cur = self.con.cursor()
        self.createTablesIfNotExist()
        self.createDirectories()

    def getConnection(self):
        return self.con
    
    def getCursor(self):
        return self.cur
    
    def createTablesIfNotExist(self):
        self.createixipornStore()

    def createixipornStore(self):
        # 0 NOTTRIED
        # 1 DOWNLOADED
        # 2 TRIED
        # 3 BLACKLISTED
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS IXIPORN_SCRAPEDCONTENTS (
                ID INTEGER PRIMARY KEY,
                TITLE TEXT NULL,
                THUMBNAILLINK TEXT UNIQUE NULL,
                VIDEOLINK TEXT UNIQUE NULL,
                DOWNLOADED INTEGER DEFAULT 0
            );""")
    
    
    def createDirectories(self):
        DIRS=[
            "downloads",
        ]

        for dir in DIRS:
            if not os.path.exists(dir):
                os.makedirs(dir)

dbinstance = DBInstance()