import os
import sqlalchemy as sql
import sqlalchemy.orm as orm

# /app $ export FLASK_APP=vetlog_rest_api
# /app $ export FLASK_ENV=development
# /app $ ~/.local/bin/flask run --host=0.0.0.0
 
from flask import Flask, g, session, redirect, url_for
from flask_session import Session  # https://pythonhosted.org/Flask-Session


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='devslkj',
    )

    # setup database connection
    user     = os.environ['MYSQL_USER']
    password = os.environ['MYSQL_PASSWORD']
    host     = os.environ['MYSQL_HOST']
    db_name  = os.environ['MYSQL_DATABASE']
    conn_str = f"mariadb+mysqlconnector://{user}:{password}@{host}/{db_name}"
    app.db_engine = sql.create_engine(conn_str, encoding='utf8', echo=True, future=True)

    #   # send commands to SQL backend: create tables if needed
    #   Base.metadata.create_all(engine)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=False)
        print('loaded config')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # init server-side session
    Session(app)

    from . import db
    db.init_app(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register blueprint: a set of views
    with app.app_context():
        # explicitely push context via with-statement to have access to current_app.config['REDIRECT_PATH']
        from . import auth
        from . import rest
        from . import demo
        app.register_blueprint(auth.bp)
        app.register_blueprint(rest.bp)
        app.register_blueprint(demo.bp)

    return app
