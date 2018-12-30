import datetime
from marshmallow import fields, Schema
from src import strings
from . import db

TRANSACTIONS_TABLE_NAME = 'transactions'

class TransactionModel(db.Model):
  """
  Transaction Model
  """
  __tablename__ = TRANSACTIONS_TABLE_NAME

  id = db.Column(db.Integer, primary_key=True)
  card_id = db.Column(db.Integer, db.ForeignKey('cards.id'))
  merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'))
  amount = db.Column(db.Float, nullable=False)
  blocked = db.Column(db.Boolean, nullable=False)
  created_at = db.Column(db.DateTime)

  def __init__(self, data):
    self.card_id = data.get(strings.CARD_ID_KEY)
    self.merchant_id = data.get(strings.MERCHANT_ID_KEY)
    self.amount = data.get(strings.AMOUNT_KEY)
    self.blocked = data.get(strings.BLOCKED_KEY)
    self.created_at = datetime.datetime.utcnow()

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
  def get_all_transactions():
    return TransactionModel.query.all()

  @staticmethod
  def get_one_transaction(id):
    return TransactionModel.query.get(id)

  @staticmethod
  def generate_transaction(card_id, merchant_id, amount, blocked=True):
    data = {}
    data[strings.CARD_ID_KEY] = card_id
    data[strings.MERCHANT_ID_KEY] = merchant_id
    data[strings.AMOUNT_KEY] = amount
    data[strings.BLOCKED_KEY] = blocked
    return TransactionModel(data)

  def __repr__(self):
    return '<id {}>'.format(self.id)

class TransactionSchema(Schema):
  """
  Transaction Schema
  """
  id = fields.Int(dump_only=True)
  card_id = fields.Int(required=True)
  merchant_id = fields.Int(required=True)
  amount = fields.Float(required=True, allow_none=False)
  blocked = fields.Boolean(required=True)
  created_at = fields.DateTime()