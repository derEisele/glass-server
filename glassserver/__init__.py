import flask
import flask_sqlalchemy
import flask_restful


app = flask.Flask(__name__)
app.config.from_json("../config.json")
#app.config["APPLICATION_ROOT"] = "/glass/"
api = flask_restful.Api(app)
db = flask_sqlalchemy.SQLAlchemy(app)

from glassserver import models
from glassserver import endpoints
#from . import infocollecter
from glassserver import media
from glassserver import setupdb

db.create_all()

api.add_resource(endpoints.Shows, "/api/shows")
api.add_resource(endpoints.Show, "/api/show")
api.add_resource(endpoints.ShowDetailed, "/api/show/<int:show_id>", "/api/shows/<int:show_id>")
api.add_resource(endpoints.EpisodeDetailed, "/api/episode/<int:episode_id>", "/api/episodes/<int:episode_id>")

def __del__():
    print("DEL")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1234, threaded=True)
