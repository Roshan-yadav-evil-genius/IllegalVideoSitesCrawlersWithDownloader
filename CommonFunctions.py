
import hashlib

def getHashOf(string):
    sha256=hashlib.sha256()
    sha256.update(string.encode('utf-8'))
    string=sha256.hexdigest()
    return str(string)