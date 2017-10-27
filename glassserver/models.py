from glassserver import db

db.create_all()
db.session.commit()

EpisodesFiles = db.Table("episodes_files",
                         db.Column('id', db.Integer, primary_key=True),
                         db.Column("episode_id", db.Integer, db.ForeignKey("episodes.id")),
                         db.Column("file_id", db.Integer, db.ForeignKey("mediafiles.id")))
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
    __table_args__ = (db.UniqueConstraint("prefix_id", "path", name="uix_1"),)

    def __init__(self, prefix_id, path):
        self.prefix_id = prefix_id
        self.path = path


db.create_all()
