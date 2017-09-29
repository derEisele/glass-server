import flask
import flask_sqlalchemy
import flask_restful


app = flask.Flask(__name__)
app.config.from_json("../config.json")
api = flask_restful.Api(app)
db = flask_sqlalchemy.SQLAlchemy(app)

from . import models
from . import endpoints
from . import infocollecter

db.create_all()
db.session.commit()

api.add_resource(endpoints.Shows, "/shows")
api.add_resource(endpoints.Show, "/show")
api.add_resource(endpoints.ShowDetailed, "/show/<int:show_id>")

def __del__():
    print("DEL")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1234, threaded=True)
