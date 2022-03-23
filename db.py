import sqlalchemy as sql
import sqlalchemy.orm as orm

from flask import g

def get_db(engine: sql.engine.Engine):
    if 'db_session' not in g:
        g.db_session = orm.Session(engine)

    return g.db_session


def close_db(e=None):
    db = g.pop('db_session', None)

    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
