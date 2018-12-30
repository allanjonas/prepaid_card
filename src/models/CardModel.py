from marshmallow import fields, Schema
from src import strings
from . import db
from .TransactionModel import TransactionSchema

CARDS_TABLE_NAME = 'cards'

class CardModel(db.Model):
  """
  Card Model
  """
  __tablename__ = CARDS_TABLE_NAME

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  card_nbr = db.Column(db.String(16), unique=True, nullable=False)
  transactions = db.relationship('TransactionModel', backref=CARDS_TABLE_NAME, lazy=True)

  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.name = data.get(strings.NAME_KEY)
    self.card_nbr = data.get(strings.CARD_NBR_KEY)

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
  def get_all_cards():
    return CardModel.query.all()

  @staticmethod
  def get_card_by_card_nbr(card_nbr):
    return CardModel.query.filter_by(card_nbr=card_nbr).first()

  @staticmethod
  def get_card(id):
    return CardModel.query.get(id)

  def __repr(self):
    return '<id {}>'.format(self.id)

class CardSchema(Schema):
  """
  Card Schema
  """
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  card_nbr = fields.Str(required=True)
  transactions = fields.Nested(TransactionSchema, many=True)
  amount = fields.Method('get_avaible_amount')
  blocked = fields.Method('get_blocked_amount')

  def get_avaible_amount(self, card):
    return self.get_total_amount(card) + -1*self.get_blocked_amount(card)

  def get_total_amount(self, card):
    return sum([x.amount for x in card.transactions if not x.blocked])

  def get_blocked_amount(self, card):
    return -1*sum([x.amount for x in card.transactions if x.blocked])
