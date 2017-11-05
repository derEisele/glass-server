"""All kinds of utils."""

from glassserver import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import ClauseElement


def get_or_create(model, **kwargs):
    """Get or create db object."""
    """from https://gist.github.com/codeb2cc/3302754"""

    print(kwargs)

    defaults = {}

    try:
        query = db.session.query(model).filter_by(**kwargs)

        instance = query.first()

        if instance:
            print("Already existing")
            return instance
        else:
            db.session.begin(nested=True)
            try:
                params = dict((k, kwargs[k]) for k in kwargs if not isinstance(kwargs[k], ClauseElement))
                #params = kwargs
                params.update(defaults)
                instance = model(**params)
                #print(instance, "is about to be added")

                db.session.add(instance)
                db.session.commit()

                return instance
            except IntegrityError as e:
                db.session.rollback()
                instance = query.first()

                return instance
    except Exception as e:
        raise e
