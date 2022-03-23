from datetime import datetime
from flask import (Blueprint, current_app, flash, jsonify, g,
                   redirect, render_template, request, session, url_for)

from .datamodel import Base, DispensedMedication, UsedMedication, object_as_dict
from . import db
from .auth import login_required

bp = Blueprint('demo', __name__, url_prefix='/demo')

@bp.route("/")
def index():
    drugs = []
    print(session.get("user"))
    if session.get("user"):
        print(g)
        engine = current_app.db_engine
        for class_instance in db.get_db(engine).query(DispensedMedication).all():
            drugs.append(class_instance)

    return render_template('demo/index.html', posts=drugs)

@bp.route('/update/<int:medication_id>', methods=['GET', 'POST'])
@login_required
def update(medication_id):
    engine = current_app.db_engine
    drugs = []
    medication = db.get_db(engine).query(DispensedMedication).get(medication_id)
    used_med = (db.get_db(engine)
                  .query(UsedMedication)
                  .filter_by(medication_id=medication_id)
                  .all())
    
    if request.method == 'POST':
        date_str = request.form['date']
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except:
            date = None
        note = request.form['note']
        error = None

        if not note:
            error = 'Menge der Anwendung fehlt.'
        elif not date:
            error = 'Datum fehlt'

        if error is not None:
            flash(error)
        else:
            new_item = UsedMedication(medication_id=medication_id, note=note, date=date)
            db.get_db(engine).add(new_item)
            db.get_db(engine).commit()
            return redirect(url_for('demo.update', medication_id=medication_id))

    return render_template('demo/update.html', medication=medication, used_med=used_med, date=datetime.now())

@bp.route('/delete_med_usage/<int:med_usage_id>', methods=['POST'])
@login_required
def delete_med_usage(med_usage_id):
    medication_id = request.form['medication_id']
    engine = current_app.db_engine
    used_med = db.get_db(engine).query(UsedMedication).get(med_usage_id)
    db.get_db(engine).delete(used_med)
    db.get_db(engine).commit()
    return redirect(url_for('demo.update', medication_id=medication_id))


@bp.route("/generate_doc")
@login_required
def generate_doc():
    engine = current_app.db_engine
    drugs = []
    for medication in db.get_db(engine).query(DispensedMedication).all():
        print(medication)
        medication_id = medication.id
        used_med = (db.get_db(engine)
                  .query(UsedMedication)
                  .filter_by(medication_id=medication_id)
                  .all())
 
        drugs.append((medication,  used_med))

    return render_template('demo/generate_doc.html', posts=drugs)


