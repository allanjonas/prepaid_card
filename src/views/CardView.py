from flask import request, json, Response, Blueprint
from src import strings
from src.models.CardModel import CardModel, CardSchema
from src.models.TransactionModel import TransactionModel, TransactionSchema

card_api = Blueprint('cards', __name__)
card_schema = CardSchema()
transaction_schema = TransactionSchema()

@card_api.route('/', methods=['GET'])
def get_all():
  cards = CardModel.get_all_cards()
  ser_cards = card_schema.dump(cards, many=True).data
  return custom_response(ser_cards, 200)

@card_api.route('/', methods=['POST'])
def create():
  """
  Create Card Function
  """
  req_data = request.get_json()
  data, error = card_schema.load(req_data)

  if error:
    return custom_response(error, 400)

  # check if card already exist in the db
  card_in_db = CardModel.get_card_by_card_nbr(data.get(strings.CARD_NBR_KEY))
  if card_in_db:
    message = {'error': 'Card number already exist, please supply another card number'}
    return custom_response(message, 400)

  card = CardModel(data)
  card.save()

  ser_data = card_schema.dump(card).data

  return custom_response({'Card': ser_data}, 201)

@card_api.route('/<int:card_id>', methods=['GET'])
def get_a_card(card_id):
  """
  Get a card
  """
  card = CardModel.get_card(card_id)
  if not card:
    return custom_response({'error': 'card not found'}, 404)
  ser_card = card_schema.dump(card).data

  del ser_card[strings.TRANSACTIONS_KEY]
  return custom_response(ser_card, 200)

@card_api.route('/<int:card_id>', methods=['DELETE'])
def delete(card_id):
  """
  Delete a card
  """
  card = CardModel.get_card(card_id)
  card.delete()
  return custom_response({'message': 'deleted'}, 204)


@card_api.route('/<int:card_id>/topup', methods=['POST'])
def topUp(card_id):
  """
  TopUp a card
  """
  req_dict = request.get_json()
  if strings.AMOUNT_KEY not in req_dict:
    return custom_response("Missing attribute \"amount\"", 400)
  if req_dict[strings.AMOUNT_KEY] <= 0:
    return custom_response("You cannot topup negative values", 403)

  card = CardModel.get_card(card_id)
  if not card:
    return custom_response({'error': 'card not found'}, 404)


  transaction = TransactionModel.generate_transaction(card_id, None, req_dict['amount'], False)
  transaction.save()
  return custom_response({'message':
    'Card with id: %s and number: %s has been topped up with %s' %
      (card_id, card.card_nbr, req_dict[strings.AMOUNT_KEY])}, 201)


@card_api.route('/<int:card_id>/transactions', methods=['GET'])
def get_a_card_transactions(card_id):
  """
  Get a card
  """
  card = CardModel.get_card(card_id)
  if not card:
    return custom_response({'error': 'card not found'}, 404)

  ser_card = card_schema.dump(card).data
  return custom_response(ser_card[strings.TRANSACTIONS_KEY], 200)

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
      mimetype="application/json",
      response=json.dumps(res),
      status=status_code
  )
