import flask
import flask_sqlalchemy
import flask_restful
from glassserver import cachetools


app = flask.Flask(__name__)
app.config.from_json("../config.json")
api = flask_restful.Api(app)
db = flask_sqlalchemy.SQLAlchemy(app)
cachetools.fromFlask(app)

from glassserver import models
from glassserver import endpoints
#from . import infocollecter
from glassserver import media
from glassserver import setupdb
from glassserver import test

db.create_all()

api.add_resource(endpoints.Shows, "/api/shows")
api.add_resource(endpoints.ShowDetailed, "/api/show/<int:show_id>", "/api/shows/<int:show_id>")
api.add_resource(endpoints.EpisodeDetailed, "/api/episode/<int:episode_id>", "/api/episodes/<int:episode_id>")

#mySong = models.Song("Test Song")
#myAlbum = models.Album("Test Album")
#myAlbum.addSong(mySong, 42)
#db.session.add_all([myAlbum, mySong])
#db.session.commit()

def __del__():
    print("DEL")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1234, threaded=True)
