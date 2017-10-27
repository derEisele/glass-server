import glassserver
from glassserver import app


app.run(host="0.0.0.0", port=1234, threaded=True)
