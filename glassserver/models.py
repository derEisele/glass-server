from glassserver import db
from datetime import timedelta, datetime

db.create_all()
db.session.commit()

EpisodesFiles = db.Table("episodes_files",
                         db.Column('id', db.Integer, primary_key=True),
                         db.Column("episode_id", db.Integer, db.ForeignKey("episodes.id")),
                         db.Column("file_id", db.Integer, db.ForeignKey("mediafiles.id")))

SongsArtists = db.Table("songs_artists",
                         db.Column('id', db.Integer, primary_key=True),
                         db.Column("artist_id", db.Integer, db.ForeignKey("artists.id")),
                         db.Column("song_id", db.Integer, db.ForeignKey("songs.id")))

AlbumsArtists = db.Table("albums_artists",
                         db.Column('id', db.Integer, primary_key=True),
                         db.Column("artist_id", db.Integer, db.ForeignKey("artists.id")),
                         db.Column("album_id", db.Integer, db.ForeignKey("albums.id")))

db.session.commit()

class Show(db.Model):

    __tablename__ = "shows"
    id = db.Column(db.Integer, primary_key=True)
    #imdb_id = db.Column(db.String(9)) TODO
    title = db.Column(db.String(100))
    year = db.Column(db.Integer)
    lang = db.Column(db.String(3))
    descr = db.Column(db.String(500))
    poster = db.Column(db.String(500))
    banner = db.Column(db.String(200))
    __table_args__ = (db.UniqueConstraint("title", "lang", "year", name="uix_1"),)



    def __init__(self, title, year, lang, descr, banner, poster):
        print("create show object", title)
        self.title = title
        self.lang = lang
        self.descr = descr
        self.banner = banner
        self.year = year
        self.poster = poster
        # self.imdb_id = imdb_id


class ShowDetailed(Show):
    seasons = db.relationship("Season")


class Season(db.Model):
    __tablename__ = "seasons"
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey("shows.id"))
    show = db.relationship("ShowDetailed", back_populates="seasons")
    season_number = db.Column(db.Integer)
    poster = db.Column(db.String(500))
    episodes = db.relationship('Episode')

    def __init__(self, show_id, season_number, poster=""):
        self.show_id = show_id
        self.season_number = season_number
        self.poster = poster


class Episode(db.Model):

    __tablename__ = "episodes"
    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey("seasons.id"))
    season = db.relationship("Season", back_populates="episodes")
    files = db.relationship("MediaFile", secondary=EpisodesFiles, backref="Episode")
    episode_number = db.Column(db.Integer)
    title = db.Column(db.String(100))
    descr = db.Column(db.String(500))
    image = db.Column(db.String(200))
    __table_args__ = (db.UniqueConstraint("season_id", "episode_number", name="uix_1"),)

    def __init__(self, season_id, episode_number, title, descr, image):
        self.season_id = season_id
        self.episode_number = episode_number
        self.title = title
        self.descr = descr
        self.image = image


class Movie(db.Model):

    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    lang = db.Column(db.String(3))
    title = db.Column(db.String(100))
    descr = db.Column(db.String(500))
    image = db.Column(db.String(200))
    year = db.Column(db.Integer)
    __table_args__ = (db.UniqueConstraint("title", "lang", "year", name="uix_1"),)

    def __init__(self, title, year, lang, descr, image):
        self.title = title
        self.lang = lang
        self.descr = descr
        self.image = image
        self.year = year


class MediaPrefix(db.Model):

    __tablename__ = "mediaprefix"
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200), unique=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Integer)

    def __init__(self, path):
        self.path = path


class MediaFile(db.Model):

    __tablename__ = "mediafiles"
    id = db.Column(db.Integer, primary_key=True)
    prefix_id = db.Column(db.Integer, db.ForeignKey("mediaprefix.id"))
    prefix = db.relationship(MediaPrefix, foreign_keys=[prefix_id])
    path = db.Column(db.String(200))
    episodes = db.relationship("Episode", secondary=EpisodesFiles, backref="MediaFile")
    viewstates = db.relationship("ViewState")
    __table_args__ = (db.UniqueConstraint("prefix_id", "path", name="uix_1"),)

    def __init__(self, prefix_id, path):
        self.prefix_id = prefix_id
        self.path = path


class Album_Song(db.Model):

    __tablename__ = "albums_songs"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    album_id = db.Column(db.Integer, db.ForeignKey("albums.id", primary_key=True))
    song_id = db.Column(db.Integer, db.ForeignKey("songs.id", primary_key=True))
    position = db.Column(db.Integer)
    disc = db.Column(db.Integer)

    album = db.relationship("Album", backref=db.backref("albums_songs", cascade="all, delete-orphan" ))
    song = db.relationship("Song", backref=db.backref("albums_songs", cascade="all, delete-orphan" ))

    def __init__(self, album=None, song=None, position=0, disc=0):
        self.album = album
        self.song = song
        self.position = position
        self.disc = disc


class Song(db.Model):

    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    artists = db.relationship("Artist", secondary=SongsArtists, backref="Song")
    year = db.Column(db.Integer)
    epCover = db.Column(db.String(200))
    albums = db.relationship("Album", secondary="albums_songs", viewonly=True)

    def __init__(self, title, year=0):
        self.title = title
        self.year = year


class Album(db.Model):

    __tablename__ = "albums"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    artists = db.relationship("Artist", secondary=AlbumsArtists, backref="Album")
    year = db.Column(db.Integer)
    cover = db.Column(db.String(200))
    songs = db.relationship("Song", secondary="albums_songs", viewonly=True)

    def __init__(self, title, year=0):
        self.title = title
        self.year = year
        self.songs = []
        self.artists = []

    def addSong(self, song, position, disc=0):
        self.albums_songs.append(Album_Song(album=self, song=song,
                                            position=position, disc=disc))


class Artist(db.Model):

    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    image = db.Column(db.String(200))
    songs = db.relationship("Song", secondary=SongsArtists, backref="Artist")
    albums = db.relationship("Album", secondary=AlbumsArtists, backref="Albums")

    def __init__(self, name, image=""):
        self.name = name
        self.image = image


class User(db.Model):

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Integer)

    def __init__(self, email, name, type=0):
        self.email = email
        self.name = name
        self.type = type


class ViewState(db.Model):
    __tablename__ = "viewstates"
    id = db.Column(db.Integer, primary_key=True)
    mediafile_id = db.Column(db.Integer, db.ForeignKey("mediafiles.id"))
    mediafile = db.relationship(MediaFile, foreign_keys=[mediafile_id], back_populates="viewstates")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User")
    completed = db.Column(db.Boolean)
    time = db.Column(db.Interval)

    def __init__(self, user_id, mediafile_id, completed=False, time=timedelta(seconds=0)):
        self.user_id = user_id
        self.mediafile_id = mediafile_id
        self.completed = completed
        self.time = time


db.create_all()
