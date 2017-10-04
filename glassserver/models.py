from glassserver import db


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
    image = db.Column(db.String(200))
    __table_args__ = (db.UniqueConstraint("title", "lang", "year", name="uix_1"),)



    def __init__(self, title, year, lang, descr, image):
        self.title = title
        self.lang = lang
        self.descr = descr
        self.image = image
        self.year = year
        #self.imdb_id = imdb_id


class ShowDetailed(Show):
    episodes = db.relationship('Episode',
                              backref=db.backref('show'))


class Episode(db.Model):

    __tablename__ = "episodes"
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey("shows.id"))
    files = db.relationship("MediaFile", secondary=EpisodesFiles, backref="episode")
    season = db.Column(db.Integer)
    episode = db.Column(db.Integer)
    title = db.Column(db.String(100))
    descr = db.Column(db.String(500))
    image = db.Column(db.String(200))
    __table_args__ = (db.UniqueConstraint("show_id", "season", "episode", name="uix_1"),)

    def __init__(self, show_id, season, episode, title, descr, image):
        self.show_id = show_id
        self.season = season
        self.episode = episode
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
    __table_args__ = (db.UniqueConstraint("prefix_id", "path", name="uix_1"),)

    def __init__(self, prefix_id, path):
        self.prefix_id = prefix_id
        self.path = path


db.create_all()
db.session.commit()
