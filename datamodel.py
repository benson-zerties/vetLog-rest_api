import sqlalchemy as sql
import os
import datetime

import sqlalchemy.orm as orm

def object_as_dict(obj):
    """Convert result to dict"""
    return {c.key: getattr(obj, c.key)
            for c in sql.inspect(obj).mapper.column_attrs}

Base = orm.declarative_base()
# Drop table
#metadata_obj = sql.MetaData()
#some_table = sql.Table("dispensed_medication", metadata_obj, autoload_with=engine)
#some_table.drop(engine)

class DispensedMedication(Base):
    __tablename__ = 'dispensed_medication'

    id = sql.Column(sql.Integer, primary_key=True)
    animal_id      = sql.Column(sql.String(64))
    animal_type    = sql.Column(sql.String(32))
    animal_quant   = sql.Column(sql.Integer)
    diagnosis      = sql.Column(sql.String(1024))
    drug           = sql.Column(sql.String(512))
    lot            = sql.Column(sql.String(512))
    usage          = sql.Column(sql.String(512))
    dispensed_only = sql.Column(sql.Integer)
    waiting_period = sql.Column(sql.String(512))
    date           = sql.Column(sql.DATETIME)

    used_medication = orm.relationship("UsedMedication", back_populates="dispensed_medication")

    def __repr__(self):
       return f"""DispensedMedication(id={self.id!r},
              animal_id={self.animal_id!r}, animal_type={self.animal_type!r}), 
              diagnosis={self.diagnosis!r}, drug={self.drug!r}, lot={self.lot}, 
              usage={self.usage!r}, dispensed_only={self.dispensed_only!r}, 
              waiting_period={self.waiting_period!r}, date={self.date})"""


class UsedMedication(Base):
    __tablename__ = 'used_medication'

    id            = sql.Column(sql.Integer, primary_key=True)
    medication_id = sql.Column(sql.ForeignKey('dispensed_medication.id'), nullable=False)
    note          = sql.Column(sql.String(512))
    date          = sql.Column(sql.DATETIME)

    dispensed_medication = orm.relationship("DispensedMedication", back_populates="used_medication")

    def __repr__(self):
        return f"""UsedMedication(id={self.id!r}, medication_id={self.medication_id!r}, 
                note={self.note!r}, date={self.date!r})"""
