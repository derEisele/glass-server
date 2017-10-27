import tvdb_api
import os
import re
from _thread import start_new_thread
from glassserver import models
from glassserver import db
from glassserver import utils
from pprint import pprint

t = tvdb_api.Tvdb(banners=True)


def indexPrefix(prefix_id, prefix):
    out = os.walk(prefix)
    found_show_dirs = dict()
    map_dir_show = dict()

    for root, dirs, files in out:
        print("Indexing", root)
        if root == prefix:
            for d in dirs:
                folder = os.path.basename(d)
                print(folder)
                name = folder.replace("-", " ")
                try:

                    myShow = getShow(name)
                    map_dir_show[d] = myShow

                except tvdb_api.tvdb_shownotfound:
                    print(name, "not found!")

        if os.path.basename(root) in map_dir_show:
            basedir = os.path.basename(root)
            show = map_dir_show[basedir]  # map dirs to show
            # show = models.Show.query.filter_by(id=show_id)

            if not files:  # If no files in folder
                print("No files in folder!")
                continue

            for f in files:
                myEpisode = getEpisode(show, f)
                path = os.path.join(root, f).replace(prefix, "")
                myMediaFile = getMediaFile(prefix_id, path)

                if myEpisode:
                    myEpisode.files.append(myMediaFile)
                else:
                    print("Skipped")

                continue


"""


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

                    if not db.session.query(models.Episode).filter_by(show_id=show_id, season_id=season_id, episode_number=episode_number).first():
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
                    print("AttributeError in show {}".format(show))
                        #raisetry:

                    except TypeError as e:
                        print(e)
                        print("{} has no episodes?!".format(show))"""

def searchTVShow(name):
    try:
        show = t[name]
        return show
    except AttributeError:
        raise tvdb_api.tvdb_shownotfound


def importAll():
    prefixes = models.MediaPrefix.query.all()
    for prefix in prefixes:
        print("Prefix", prefix.path)
        #start_new_thread(indexPrefix, (prefix.id, prefix.path))
        indexPrefix(prefix.id, prefix.path)


def parseEpisodeFileName(fileName):
    """Return season and episode as tuple or raise episodenotfound exception."""
    print("Parsing", fileName)
    if re.match("(\w|-|_)*\d+(E|x)\d+(\w|-|_)*.(mp4|mkv|flv)", fileName):
        # The-Example-Show_S03E07_An-Episode.mkv
        match = re.search("\d+(E|x)\d+", fileName).group(0)
        print(match)
        # 03E07
        tmp = re.findall("\d+", match)
        # [03, 07]
        return (int(tmp[0]), int(tmp[1]))
    else:
        raise SyntaxError


def getShow(showTitle):
    """Return Show Object and inserts it into db if needed."""
    """Raises shownotfound exception"""
    tvdb_show = searchTVShow(showTitle)

    title = tvdb_show.data['seriesName']
    lang = tvdb_show.data["language"]

    descr = tvdb_show.data["overview"]
    if descr:
        descr = descr[:500]

    year = tvdb_show.data["firstAired"][:4]
    if year == "" or year == " ":
        year = 0000
    # print(year)

    banner = tvdb_show.data["banner"]
    # print(show_data.data["_banners"]["poster"]["raw"][0]["fileName"])

    poster = ""
    if tvdb_show.data.get("_banners"):
        if tvdb_show.data["_banners"].get("poster"):
            poster = tvdb_show.data["_banners"]["poster"]["raw"][0]["fileName"]
            if poster:
                poster = "https://www.thetvdb.com/banners/" + poster

    show = utils.get_or_create(models.ShowDetailed,
                               title=title,
                               lang=lang,
                               descr=descr,
                               year=year,
                               banner=banner,
                               poster=poster)
    db.session.commit()
    return show


def getEpisode(show, fileName):
    """Return Show Object and inserts it into db if needed."""
    try:

        (season_number, episode_number) = parseEpisodeFileName(fileName)

        tvdb_query = t[show.title][season_number][episode_number]
        title = tvdb_query["episodename"]
        image = tvdb_query["banner"]
        if image:
            image = "https://api.thetvdb.com/" + image

        descr = tvdb_query["overview"]
        if descr:
            descr = descr[:500]

        season = utils.get_or_create(models.Season,
                                     show_id=show.id,
                                     season_number=season_number,
                                     poster="")
        db.session.commit()

        episode = utils.get_or_create(models.Episode,
                                      season_id=season.id,
                                      episode_number=episode_number,
                                      title=title,
                                      descr=descr,
                                      image=image)

        db.session.commit()

        print("Episode ID", episode.id)
        return episode

    except tvdb_api.tvdb_seasonnotfound:
        print("Season {} of {} not found!".format(season_number, show.title))

    except tvdb_api.tvdb_episodenotfound:
        print("S{}E{} of {} not found!".format(season_number, episode_number, show.title))

    except SyntaxError:
        print("{} has invalid syntax!".format(fileName))


def getMediaFile(prefix_id, path):
    """Requires prefix ID and path without prefix."""

    mediafile = utils.get_or_create(models.MediaFile,
                                    prefix_id=prefix_id,
                                    path=path)
    db.session.commit()
    return mediafile


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
