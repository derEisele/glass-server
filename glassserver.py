import flask
import flask_sqlalchemy
import flask_restless

app = flask.Flask(__name__)
app.config.from_json("config.json")
db = flask_sqlalchemy.SQLAlchemy(app)


class Show(db.Model):

    __tablename__ = "shows"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    lang = db.Column(db.String(3))
    descr = db.Column(db.String(200))
    image = db.Column(db.String(200))

    def __init__(self, title, lang, descr, image):
        self.title = title
        self.lang = lang
        self.descr = descr
        self.image = image


class ShowDetailed(Show):
    episode = db.relationship('Episode',
                              backref=db.backref('show'))


class Episode(db.Model):

    __tablename__ = "episodes"
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey("shows.id"))
    season = db.Column(db.Integer)
    episode = db.Column(db.Integer)
    descr = db.Column(db.String(200))
    image = db.Column(db.String(200))

    def __init__(self, show_id, season, episode, descr, image):
        self.show_id = 0
        self.season = 0
        self.episode = 0
        self.descr = descr
        self.image = image


db.create_all()
db.session.commit()
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Show)
manager.create_api(ShowDetailed, collection_name="showsdetailed")
manager.create_api(Episode, exclude_columns=["show_id"])

if __name__ == "__main__":
    sh = Show("testShow", "en", "test show", "linktoimg")
    sh_id = Show.query.get(id)
    print(id)
    ep = Episode("3", "2", "3", "test episode", "linktoimg")
    #db.session.add(sh)
    #db.session.add(ep)
    db.session.commit()
    app.run(host="0.0.0.0", port=1234)
