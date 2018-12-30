from flask import request, json, Response, Blueprint
from src import strings
from src.models.MerchantModel import MerchantModel, MerchantSchema
from src.models.CardModel import CardModel, CardSchema
from src.models.TransactionModel import TransactionModel, TransactionSchema

merchant_api = Blueprint('merchants', __name__)
merchant_schema = MerchantSchema()
card_schema = CardSchema()
transaction_schema = TransactionSchema()

def _check_request_and_get_transaction(req_data, merchant_id):
  if strings.TRANSACTIONS_ID_KEY not in req_data:
    return None, custom_response({'error': 'Missing transaction attribute'}, 400)
  if strings.AMOUNT_KEY not in req_data:
    return None, custom_response({'error': 'Missing amount attribute'}, 400)
  if req_data[strings.AMOUNT_KEY] < 0:
    return None, custom_response({'error': 'amount is value is incorrect'}, 400)

  transaction = TransactionModel.get_one_transaction(req_data[strings.TRANSACTIONS_ID_KEY])
  if not transaction or transaction.merchant_id != merchant_id or not transaction.blocked:
    return None, custom_response({'error': 'The transaction_id is not correct for this Merchant'}, 404)
  return transaction, None

def _check_request_and_get_merchant_and_card(req_data, merchant_id):
  if strings.CARD_NBR_KEY not in req_data:
    return None, None, custom_response({'error': 'Missing card_nbr attribute'}, 400)
  if strings.AMOUNT_KEY not in req_data:
    return None, None, custom_response({'error': 'Missing amount attribute'}, 400)
  if req_data[strings.AMOUNT_KEY] <= 0:
    return None, None, custom_response({'error': 'amount is value is incorrect'}, 400)

  merchant = MerchantModel.get_one_merchant(merchant_id)
  if not merchant:
    return None, None, custom_response({'error': 'merchant not found'}, 404)

  card = CardModel.get_card_by_card_nbr(req_data[strings.CARD_NBR_KEY])
  if not card:
    return None, None, custom_response({'error': 'card number was not found'}, 404)
  return merchant, card, None

@merchant_api.route('/', methods=['GET'])
def get_all():
  merchants = MerchantModel.get_all_merchants()
  ser_merchants = merchant_schema.dump(merchants, many=True).data
  return custom_response(ser_merchants, 200)

@merchant_api.route('/', methods=['POST'])
def create():
  """
  Create User Function
  """
  req_data = request.get_json()
  data, error = merchant_schema.load(req_data)

  if error:
    return custom_response(error, 400)

  # check if user already exist in the db
  user_in_db = MerchantModel.get_merchant_by_name(data.get(strings.NAME_KEY))
  if user_in_db:
    message = {'error': 'Merchant with that name already exist, please choose another'}
    return custom_response(message, 400)

  merchant = MerchantModel(data)
  merchant.save()

  ser_data = merchant_schema.dump(merchant).data

  return custom_response({'Merchant': ser_data}, 201)

@merchant_api.route('/<int:merchant_id>', methods=['DELETE'])
def delete(merchant_id):
  """
  Delete a merchant
  """
  merchant = MerchantModel.get_one_merchant(merchant_id)
  for transaction in merchant.transactions:
    if transaction.blocked:
      transaction.delete()
  merchant.delete()
  return custom_response({'message': 'deleted'}, 204)

@merchant_api.route('/<int:merchant_id>', methods=['GET'])
def get_merchant_info(merchant_id):
  merchant = MerchantModel.get_one_merchant(merchant_id)
  if not merchant:
    return custom_response({'error': 'merchant not found'}, 404)

  ser_merchant = merchant_schema.dump(merchant).data
  return custom_response(ser_merchant, 200)

@merchant_api.route('/<int:merchant_id>/capture', methods=['POST'])
def capture(merchant_id):
  req_data = request.get_json()
  transaction, error = _check_request_and_get_transaction(req_data, merchant_id)
  if error:
    return error

  if transaction.amount + req_data[strings.AMOUNT_KEY] > 0:
    return custom_response({'error': 'The request amount is more than the existing amount in the transaction'}, 403)
  if transaction.amount + req_data[strings.AMOUNT_KEY] != 0:
    transaction.amount = transaction.amount + req_data[strings.AMOUNT_KEY]
    transaction_blocked = TransactionModel.generate_transaction(transaction.card_id, merchant_id, -1*req_data[strings.AMOUNT_KEY], False)
    transaction_blocked.created_at = transaction.created_at
    transaction_blocked.save()
    transaction.save()
  else:
    transaction.blocked = False
    transaction.save()
  ser_transaction = transaction_schema.dump(transaction).data
  return custom_response({'Transaction':  ser_transaction}, 200)

@merchant_api.route('/<int:merchant_id>/reverse', methods=['POST'])
def reverse(merchant_id):
  req_data = request.get_json()
  transaction, error = _check_request_and_get_transaction(req_data, merchant_id)
  if error:
    return error

  if transaction.amount + req_data[strings.AMOUNT_KEY] > 0:
    return custom_response({'error': 'Cannot reverse more than was authorized'}, 400)
  elif transaction.amount + req_data[strings.AMOUNT_KEY] < 0:
    transaction.amount += req_data[strings.AMOUNT_KEY]
    transaction.save()
  else:
    transaction.delete()
  return custom_response({'Reverse':  "Ok"}, 201)

@merchant_api.route('/<int:merchant_id>/auth_request', methods=['POST'])
def create_auth_request(merchant_id):
  req_data = request.get_json()
  merchant, card, error = _check_request_and_get_merchant_and_card(req_data, merchant_id)
  if error:
    return error

  ser_card = card_schema.dump(card).data
  ser_merchant = merchant_schema.dump(merchant).data
  print(merchant_id)
  if ser_card[strings.AMOUNT_KEY] < req_data[strings.AMOUNT_KEY]:
    return custom_response({'error': 'Not enough card amount'}, 400)

  transaction = TransactionModel.generate_transaction(card.id, merchant_id, -1*req_data[strings.AMOUNT_KEY])
  transaction.save()
  ser_transaction = transaction_schema.dump(transaction).data
  return custom_response({'Transaction':  ser_transaction}, 201)


@merchant_api.route('/<int:merchant_id>/refund', methods=['POST'])
def refund(merchant_id):
  req_data = request.get_json()
  merchant, card, error = _check_request_and_get_merchant_and_card(req_data, merchant_id)
  if error:
    return error

  available_refund = sum([x.amount for x in merchant.transactions if x.card_id == card.id and not x.blocked])
  if req_data[strings.AMOUNT_KEY] + available_refund > 0:
     return custom_response({'error': 'trying to refund more than is refundable'}, 403)
  transaction = TransactionModel.generate_transaction(card.id, merchant_id, req_data[strings.AMOUNT_KEY], False)
  transaction.save()
  ser_transaction = transaction_schema.dump(transaction).data
  return custom_response({'Transaction':  ser_transaction}, 201)

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
      mimetype="application/json",
      response=json.dumps(res),
      status=status_code
  )