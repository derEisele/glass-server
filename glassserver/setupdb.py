from glassserver.models import *
from glassserver import db

db.create_all()
db.session.commit()
