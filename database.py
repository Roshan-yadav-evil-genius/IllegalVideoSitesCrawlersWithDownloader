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
        self.createUncutJalwaStore()
        self.createUncutMazaStore()
        self.createUniqueUrlTable()
        self.createurlMappingTable()

    def createUncutJalwaStore(self):
        # 0 FALSE
        # 1 TRUE
        # 2 TRIED
        # 3 BLACKLISTED
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS UNCUTJALWA_SCRAPEDCONTENTS (
                ID INTEGER PRIMARY KEY,
                TITLE TEXT NULL,
                THUMBNAILLINK TEXT UNIQUE NULL,
                VIDEOLINK TEXT UNIQUE NULL,
                DOWNLOADED INTEGER DEFAULT 1,
                EXPORTED BOOLEAN DEFAULT FALSE,
                SOURCE TEXT NULL
            ); """)
        
    def createUncutMazaStore(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS UNCUTMAZA_SCRAPEDCONTENTS (
                ID INTEGER PRIMARY KEY,
                TITLE TEXT NULL,
                THUMBNAILLINK TEXT UNIQUE NULL,
                VIDEOLINK TEXT UNIQUE NULL,
                DOWNLOADED INTEGER DEFAULT 0,
                EXPORTED BOOLEAN DEFAULT FALSE,
                SOURCE TEXT NULL
            ); """)
        
    def createurlMappingTable(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS CRAWLER_LIFECYCLE (
                ID INTEGER PRIMARY KEY,
                FROMURL TEXT NULL,
                URL TEXT NULL,
                UNIQUE(FROMURL, URL)
                FOREIGN KEY (FROMURL) REFERENCES URLSTORE(ID),
                FOREIGN KEY (URL) REFERENCES URLSTORE(ID)
            ); """)

    def createUniqueUrlTable(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS URLSTORE (
                ID INTEGER PRIMARY KEY,
                URL TEXT UNIQUE,
                STATUS BOOLEAN DEFAULT FALSE
            ); """)
    
    def createDirectories(self):
        DIRS=[
            "downloads",
            "Export",
            "Export/image",
            "Export/video"
        ]

        for dir in DIRS:
            if not os.path.exists(dir):
                os.makedirs(dir)

dbinstance = DBInstance()