import os

CACHE_DIR = "cache"


def setPath(myPath):
    global CACHE_DIR
    CACHE_DIR = myPath


def fromFlask(app):
    global CACHE_DIR
    CACHE_DIR = os.path.join(os.path.dirname(__file__),
                             app.config.get("GLASS_CACHE", "../cache_default"))
