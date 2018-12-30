
import os
import sys
sys.path.insert(0, os.path.abspath('../'))
import unittest
import json
from src.models import db
from src.app import create_app
from src import strings

TEST_DB = os.getenv('TEST_DATABASE_URL')

class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app = create_app('development')
        app.testing = True
        app.debug = False
        self.app = app.test_client()
        self.app.application.config['SQLALCHEMY_DATABASE_URI'] = TEST_DB
        with app.app_context():
            db.drop_all()
            db.create_all()
        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
      pass

    def get_cards(self):
      rv = self.app.get(strings.CARD_ENDPOINT, follow_redirects=True)
      self.assertEqual(rv.status_code, 200)
      return rv

    def create_card(self, name, card_nbr, expected_response_code):
      rv = self.app.post(strings.CARD_ENDPOINT,
                    json={strings.NAME_KEY:name, strings.CARD_NBR_KEY:card_nbr})
      self.assertEqual(rv.status_code, expected_response_code)
      return rv

    def top_up_card(self, card_id, amount, expected_response_code):
      rv = self.app.post(strings.CARD_ENDPOINT+str(card_id)+"/topup",
                              json={strings.AMOUNT_KEY: amount})
      self.assertEqual(rv.status_code, expected_response_code)
      return rv

    def delete_card(self, card_id, expected_response_code):
      rv = self.app.delete(strings.CARD_ENDPOINT+str(card_id))
      self.assertEqual(rv.status_code, expected_response_code)
      return rv

    def get_merchants(self):
      rv = self.app.get(strings.MERCHANT_ENDPOINT, follow_redirects=True)
      self.assertEqual(rv.status_code, 200)
      return rv

    def create_merchant(self, name, expected_response_code):
      rv = self.app.post(strings.MERCHANT_ENDPOINT, json={strings.NAME_KEY:name})
      self.assertEqual(rv.status_code, expected_response_code)
      return rv

    def delete_merchant(self, merchant_id, expected_response_code):
      rv = self.app.delete(strings.MERCHANT_ENDPOINT+str(merchant_id))
      self.assertEqual(rv.status_code, expected_response_code)
      return rv

    def create_auth_request(self, merchant_id, card_nbr, amount, expected_response_code):
      rv = self.app.post(strings.MERCHANT_ENDPOINT+str(merchant_id)+"/auth_request",
      json={strings.CARD_NBR_KEY: card_nbr, strings.AMOUNT_KEY: amount})
      self.assertEqual(rv.status_code, expected_response_code)
      return rv

    def capture(self, merchant_id, transaction_id, amount, expected_response_code):
      rv = self.app.post(strings.MERCHANT_ENDPOINT+str(merchant_id)+"/capture",
      json={strings.TRANSACTIONS_ID_KEY: transaction_id, strings.AMOUNT_KEY: amount})
      self.assertEqual(rv.status_code, expected_response_code)
      return rv

    def reverse(self, merchant_id, transaction_id, amount, expected_response_code):
      rv = self.app.post(strings.MERCHANT_ENDPOINT+str(merchant_id)+"/reverse",
      json={strings.TRANSACTIONS_ID_KEY: transaction_id, strings.AMOUNT_KEY: amount})
      self.assertEqual(rv.status_code, expected_response_code)
      return rv

    def refund(self, merchant_id, card_nbr, amount, expected_response_code):
      rv = self.app.post(strings.MERCHANT_ENDPOINT+str(merchant_id)+"/refund",
      json={strings.CARD_NBR_KEY: card_nbr, strings.AMOUNT_KEY: amount})
      self.assertEqual(rv.status_code, expected_response_code)
      return rv

    def check_first_card(self, expected_name, expected_card_nbr, expected_amount, expected_blocked):
      response = self.get_cards()
      data = json.loads(response.get_data().decode())[0]
      self.assertEqual(data[strings.NAME_KEY], expected_name)
      self.assertEqual(data[strings.CARD_NBR_KEY], expected_card_nbr)
      self.assertEqual(data[strings.AMOUNT_KEY], expected_amount)
      self.assertEqual(data[strings.BLOCKED_KEY], expected_blocked)

    def test_create_card_and_top_up(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      response = self.create_card(name, card_nbr, 201)

      #Get cards
      self.check_first_card(name, card_nbr, 0, 0)

      #TopUp
      amount = 5.4
      response = self.top_up_card(1, amount, 201)

      #Check that the card has been credited
      self.check_first_card(name, card_nbr, amount, 0)

    def test_create_and_delete_card(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      response = self.create_card(name, card_nbr, 201)

      amount = 5.4
      response = self.top_up_card(1, amount, 201)

      #Get cards
      self.check_first_card(name, card_nbr, amount, 0)

      self.delete_card(1, 204)

    def test_top_up_non_existing(self):
      amount = 5.4
      card_id = 1
      response = self.top_up_card(card_id, amount, 404)

    def test_top_up_negative(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      response = self.create_card(name, card_nbr, 201)

      #Get cards
      self.check_first_card(name, card_nbr, 0, 0)

      #Topup
      amount = -100
      response = self.top_up_card(1, amount, 403)

      #Check that card is unchanged
      self.check_first_card(name, card_nbr, 0, 0)

    def test_create_merchant(self):
      #Create merchant
      name = "CoffeMaker"
      response = self.create_merchant(name, 201)

      #Check that merchant exists
      response = self.get_merchants()
      data = json.loads(response.get_data().decode())[0]
      self.assertEqual(data[strings.NAME_KEY], name)

    def test_create_and_delete_merchant(self):
      #Create merchant
      name = "CoffeMaker"
      response = self.create_merchant(name, 201)

      #Check that merchant exists
      response = self.get_merchants()
      data = json.loads(response.get_data().decode())[0]
      self.assertEqual(data[strings.NAME_KEY], name)

      self.delete_merchant(1, 204)

    def test_top_up_and_auth_requst(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      amount = 5.4
      auth_sum = 5
      response = self.create_card(name, card_nbr, 201)

      #TopUp
      response = self.top_up_card(1, amount, 201)

      #Create merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Generate an auth_request
      response = self.create_auth_request(1, card_nbr, auth_sum, 201)

      #Check that the amount has been blocked
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum)

    def test_auth_request_top_up_auth_request(self):
      #Create_card
      name = "Test user"
      card_nbr = "123456"
      amount = 5.4
      auth_sum = 5
      response = self.create_card(name, card_nbr, 201)

      #Create merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      # Try auth_request on a card without enough cash
      response = self.create_auth_request(1, card_nbr, auth_sum, 400)

      #Check that the card has not been deducted
      self.check_first_card(name, card_nbr, 0, 0)

      #TopUp the card
      response = self.top_up_card(1, amount, 201)

      #Generate an auth_request
      response = self.create_auth_request(1, card_nbr, auth_sum, 201)

      #Check that the amount has been blocked
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum)

    def test_top_up_auth_request_caputre(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      amount = 5.4
      auth_sum = 5
      capture_sum = 3
      response = self.create_card(name, card_nbr, 201)

      #TopUp
      response = self.top_up_card(1, amount, 201)

      #Create merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Create auth_request
      response = self.create_auth_request(1, card_nbr, auth_sum, 201)

      #Check that the correct amount is blocked
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum)

      #Capture
      response = self.capture(1, 2, capture_sum, 200)

      #Check that the blocked amount has changed
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum - capture_sum)

    def test_capture_more_than_an_auth_req(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      amount = 5.4
      auth_sum = 5
      capture_sum = 10
      response = self.create_card(name, card_nbr, 201)

      #TopUp
      response = self.top_up_card(1, amount, 201)

      #Create Merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Create auth_request
      response = self.create_auth_request(1, card_nbr, auth_sum, 201)

      #Capture more that available
      response = self.capture(1, 2, capture_sum, 403)

    def test_multiple_captures(self):
      #Create user
      name = "Test user"
      card_nbr = "123456"
      amount = 5
      auth_sum = 5
      capture_sum = 1
      response = self.create_card(name, card_nbr, 201)

      #TopUp
      response = self.top_up_card(1, amount, 201)

      #Create Merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Create auth_request
      response = self.create_auth_request(1, card_nbr, amount, 201)

      #Try multiple captures
      for i in range(auth_sum):
        self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum - (i * capture_sum))
        response = self.capture(1, 2, capture_sum, 200)

      #Try capture when there is not enought cash left
      response = self.capture(1, 2, capture_sum, 404)

    def test_capture_from_another_merchant(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      amount = 5
      auth_sum = 5
      capture_sum = 1
      response = self.create_card(name, card_nbr, 201)

      #TopUp
      response = self.top_up_card(1, amount, 201)

      #Create merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Generate auth_request
      response = self.create_auth_request(1, card_nbr, auth_sum, 201)

      #Create another merchant
      secound_merchant_name = "TeaCreater"
      response = self.create_merchant(secound_merchant_name, 201)

      #Try capture with wrong merchant
      response = self.capture(2 ,1 , capture_sum, 404)

    def test_reverse(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      amount = 5.4
      auth_sum = 5
      reverse_sum = 3
      response = self.create_card(name, card_nbr, 201)

      #TopUp
      response = self.top_up_card(1, amount, 201)

      #Create merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Create auth_request
      response = self.create_auth_request(1, card_nbr, auth_sum, 201)

      #Check that the correct amount is blocked
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum)

      #Reverse
      response = self.reverse(1, 2, reverse_sum, 201)

      #Check that the blocked amount has changed
      self.check_first_card(name, card_nbr, amount - auth_sum + reverse_sum, auth_sum - reverse_sum)


    def test_reverse_more_than_a_auth_req(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      amount = 5.4
      auth_sum = 5
      reverse_sum = 5.1
      response = self.create_card(name, card_nbr, 201)
      #TopUp
      response = self.top_up_card(1, amount, 201)

      #Create merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Create auth_request
      response = self.create_auth_request(1, card_nbr, auth_sum, 201)

      #Check that the correct amount is blocked
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum)

      #Reverse
      response = self.reverse(1, 2, reverse_sum, 400)

      #Check that the blocked amount has changed
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum)

    def test_reverse_from_another_merchant(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      amount = 5
      auth_sum = 5
      capture_sum = 1
      response = self.create_card(name, card_nbr, 201)

      #TopUp
      response = self.top_up_card(1, amount, 201)

      #Create merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Generate auth_request
      response = self.create_auth_request(1, card_nbr, auth_sum, 201)

      #Create another merchant
      secound_merchant_name = "TeaCreater"
      response = self.create_merchant(secound_merchant_name, 201)

      #Try capture with wrong merchant
      response = self.reverse(2 ,1 , capture_sum, 404)

    def test_multiple_reverses(self):
      #Create user
      name = "Test user"
      card_nbr = "123456"
      amount = 5
      auth_sum = 5
      reverse_sum = 1
      response = self.create_card(name, card_nbr, 201)

      #TopUp
      response = self.top_up_card(1, amount, 201)

      #Create Merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Create auth_request
      response = self.create_auth_request(1, card_nbr, amount, 201)

      #Try multiple captures
      for i in range(auth_sum):
        self.check_first_card(name, card_nbr, amount - auth_sum + (i * reverse_sum), auth_sum - (i * reverse_sum))
        response = self.reverse(1, 2, reverse_sum, 201)

      #Try capture when there is not enought cash left
      response = self.reverse(1, 2, reverse_sum, 404)

    def test_refund(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      amount = 5.4
      auth_sum = 5
      capture_sum = 3
      response = self.create_card(name, card_nbr, 201)

      #TopUp
      response = self.top_up_card(1, amount, 201)

      #Create merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Create auth_request
      response = self.create_auth_request(1, card_nbr, auth_sum, 201)

      #Check that the correct amount is blocked
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum)
      response = self.get_cards()

      #Capture
      response = self.capture(1, 2, capture_sum, 200)

      #Check that the blocked amount has changed
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum - capture_sum)

      #Refund
      response = self.refund(1, card_nbr, capture_sum, 201)

      #Check that the amount is refunded
      self.check_first_card(name, card_nbr, amount - auth_sum + capture_sum, auth_sum - capture_sum)


    def test_refund_more_than_sold(self):
      #Create card
      name = "Test user"
      card_nbr = "123456"
      amount = 5.4
      auth_sum = 5
      capture_sum = 3
      refund_sum = 4
      response = self.create_card(name, card_nbr, 201)

      #TopUp
      response = self.top_up_card(1, amount, 201)

      #Create merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Create auth_request
      response = self.create_auth_request(1, card_nbr, auth_sum, 201)

      #Check that the correct amount is blocked
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum)

      #Capture
      response = self.capture(1, 2, capture_sum, 200)

      #Check that the blocked amount has changed
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum - capture_sum)

      #Refund
      response = self.refund(1, card_nbr, refund_sum, 403)

      #Check that the amount is refunded
      self.check_first_card(name, card_nbr, amount - auth_sum, auth_sum - capture_sum)

    def test_refund_non_existing_card(self):
      card_nbr = "123456"
      #Create merchant
      merchant_name = "CoffeMaker"
      response = self.create_merchant(merchant_name, 201)

      #Refudn non existing card
      response = self.refund(1, card_nbr, 3, 404)

if __name__ == "__main__":
    unittest.main()