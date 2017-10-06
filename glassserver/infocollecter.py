import tvdb_api
import os
import re
from _thread import start_new_thread
from . import models
from . import db
from pprint import pprint

t = tvdb_api.Tvdb()


def indexPrefix(prefix_id, prefix):
    out = os.walk(prefix)
    found_show_dirs = dict()
    for root, dirs, files in out:
        if root == prefix:
            for d in dirs:
                folder = os.path.basename(d)
                print(folder)
                name = folder.replace("-", " ")
                try:
                    rs = searchTVShow(name)
                    title = rs[0]["seriesName"]
                    lang = rs[0]["language"]
                    descr = rs[0]["overview"]
                    if descr:
                        descr = descr[:500]
                    year = rs[0]["firstAired"][:4]
                    if year == "" or year == " ":
                        year = 0000
                    print(year)
                    image = rs[0]["banner"]
                    if image:
                        image = "https://api.thetvdb.com/" + image

                    existing_show = db.session.query(models.Show).filter_by(title=title, lang=lang, year=year).first()
                    if not existing_show:
                        db_show = models.Show(title, year, lang, descr, image)
                        db.session.add(db_show)
                        db.session.commit()

                        found_show_dirs[d] = (db_show.id, db_show.title)
                        #currentShow = title
                    else:
                        found_show_dirs[d] = (existing_show.id, existing_show.title)

                except tvdb_api.tvdb_shownotfound:
                    print(name, "not found!")

        if os.path.basename(root) in found_show_dirs:
            basedir = os.path.basename(root)
            show = found_show_dirs[basedir]
            #print(found_show_dirs[basedir])
            pprint(show)
            if not files:
                continue

            for f in files:
                if re.match("(\w|-|_)*\d+(E|x)\d+(\w|-|_)*.(mp4|mkv|flv)", f):
                    # The-Example-Show_S03E07_An-Episode.mkv
                    match = re.search("\d+(E|x)\d+", f)[0]
                    # 03E07
                    tmp = re.findall("\d+", match)
                    # [03, 07]
                    (season, episode) = (int(tmp[0]), int(tmp[1]))

                    try:
                        rs = t[show[1]][season][episode]
                        title = rs["episodename"]
                        image = rs["banner"]
                        if image:
                            image = "https://api.thetvdb.com/" + image
                        descr = rs["overview"]
                        if descr:
                            descr = descr[:500]
                        #show_id = db.session.query(models.Show).filter_by(title=show).first().id
                        show_id = show[0]

                        print(root)
                        path = os.path.join(root, f).replace(prefix, "")

                        db_file = db.session.query(models.MediaFile).filter_by(prefix_id=prefix_id, path=path).first()

                        if not db_file:
                            db_file = models.MediaFile(prefix_id, path)
                            db.session.add(db_file)
                            db.session.commit()

                        file_id = db_file.id

                        if not db.session.query(models.Episode).filter_by(show_id=show_id, season=season, episode=episode).first():
                            db_episode = models.Episode(show_id, season, episode, title, descr, image)
                            db_episode.files.append(db_file)
                            db.session.add(db_episode)
                            db.session.commit()
                            print(db_episode.id)


                    except tvdb_api.tvdb_seasonnotfound:
                        print("Season {} of {} not found!".format(season, show))

                    except tvdb_api.tvdb_episodenotfound:
                        print("S{}E{} of {} not found!".format(season, episode, show))

                    except AttributeError:
                        raise

                    except TypeError as e:
                        print(e)
                        print("{} has no episodes?!".format(show))

def searchTVShow(name):
    results = t.search(name)
    return results

def importAll():
    prefixes = models.MediaPrefix.query.all()
    for prefix in prefixes:
        start_new_thread(indexPrefix, (prefix.id, prefix.path))
        #indexPrefix(prefix.id, prefix.path)


if __name__ == "__main__":
    print("Testing mode")
    """
    print("search for show")
    search_in = input()
    print("Searching for", search_in)
    rs = searchTVShow(search_in)
    pprint(rs)
    """
    indexPrefix("/media/hdd1/TV/shows")
    #pprint(list(f))
