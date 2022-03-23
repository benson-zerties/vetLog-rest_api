from datetime import datetime
from flask import (Blueprint, current_app, jsonify,
                   redirect, render_template, session, url_for)

from .datamodel import Base, DispensedMedication, UsedMedication, object_as_dict
from . import db
from .auth import login_required

bp = Blueprint('rest', __name__)

@bp.route("/")
def index():
    if not session.get("user"):
        #session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
        #auth_url=session["flow"]["auth_uri"]
        #return redirect(auth_url)
        return redirect(url_for("auth.login"))

    return 'hello world'
#    return render_template('index.html', user=session["user"], version='0')

# a simple page that says hello
@bp.route('/hello')
@login_required
def hello():
    engine = current_app.db_engine
    drugs = []
    for class_instance in db.get_db(engine).query(DispensedMedication).all():
        drugs.append(class_instance)

    print(object_as_dict(drugs[0]))
    return jsonify([object_as_dict(d) for d in drugs])

@bp.route('/get_by_date/<int:start>_<int:end>')
@login_required
def get_by_date(start, end):
    start_date = datetime.fromtimestamp(start)
    end_date = datetime.fromtimestamp(end)

    engine = current_app.db_engine
    drugs = []
    for class_instance in (db.get_db(engine)
                            .query(DispensedMedication)
                            .filter(DispensedMedication.date.between(start_date, end_date))
                            .all()
                           ):
        drugs.append(class_instance)

    return jsonify([object_as_dict(d) for d in drugs])
