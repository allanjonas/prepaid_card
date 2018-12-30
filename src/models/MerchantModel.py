from marshmallow import fields, Schema
from src import strings
from . import db
from .TransactionModel import TransactionSchema

MERCHANTS_TABLE_NAME = 'merchants'

class MerchantModel(db.Model):
  """
  Merchant Model
  """
  __tablename__ = MERCHANTS_TABLE_NAME

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False, unique=True)
  transactions = db.relationship('TransactionModel', backref=MERCHANTS_TABLE_NAME, lazy=True)

  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.name = data.get(strings.NAME_KEY)

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all_merchants():
    return MerchantModel.query.all()

  @staticmethod
  def get_one_merchant(id):
    return MerchantModel.query.get(id)

  @staticmethod
  def get_merchant_by_name(name):
    return MerchantModel.query.filter_by(name=name).first()

  def __repr(self):
    return '<id {}>'.format(self.id)


class MerchantSchema(Schema):
  """
  Merchant Schema
  """
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  transactions = fields.Nested(TransactionSchema, many=True)
