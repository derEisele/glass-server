from . import models
from . import db
from pprint import pprint
from _thread import start_new_thread
import os
import re
import tvdb_api

t = tvdb_api.Tvdb()

prefixes = models.MediaPrefix.query.all()


def searchTVShow(name):
    r_show = t.search(name)
    pprint(r_show)


def importPath(prefix_id, path):
    print(path)
    elements = os.listdir(path)

    for element in elements:
        currentPath = os.path.join(path, element)
        if os.path.isdir(currentPath):
            start_new_thread(importShowPath, (prefix_id, path, element))


def importShowPath(prefix_id, prefix, path):
    currentPath = os.path.join(prefix, path)

    show = ia.search_for_title(path.replace("-", " "))
    if show:
        pprint(show[0].update)
        title = show[0]["title"]
        year = show[0]["year"]
        imdb_id = show[0]["imdb_id"]
        plot = ia.get_title_plots(show[0]["imdb_id"])
        if len(plot) == 0:
            plot = ""
        else:
            plot = plot[0][0:500]
        image = ""
        lang = "en"  # TODO
        dbshow = models.Show(str(title), str(year), lang, str(plot), image, str(imdb_id))
        instance = db.session.query(models.Show).filter_by(title=dbshow.title, lang=dbshow.lang, year=dbshow.year).first()
        if not instance:
            db.session.add(dbshow)
            print("Added", dbshow.title)



        elements2 = os.listdir(currentPath)
        for e in elements2:
            if os.path.isfile(os.path.join(currentPath, e)):
                if re.match("(\w|-|_)*\d+(E|x)\d+(\w|-|_)*.(mp4|mkv|flv)", e):
                    #importEpisode(prefix_id, imdb_id, currentPath, e)
                    print("matched", e)
                else:
                    print("missed", e)



    else:
        print(path, "not found!")
    db.session.commit()


def importEpisode(prefix_id, imdb_id, path, file):
    match = re.search("\d+(E|x)\d+", file)[0]
    tmp = re.findall("\d+", match)
    (season, episode) = (tmp[0], tmp[1])
    allEps = ia.get_movie(imdb_id)
    pprint(allEps)


for prefix in prefixes:
    start_new_thread(importPath, (prefix.id, prefix.path))
