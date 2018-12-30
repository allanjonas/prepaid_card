# Simple Prepaid card

A simplified model of a prepaid card API where you create cards and merchants with following actions:
- Create card
- Top up card
- Create Merchant
- Authorization request of a card
- Capture
- Reverse
- Refund

> You can try it out using the host: https://prepaidcard.herokuapp.com/

## Requirements
 - Python 3
 - Postgresql
---


## Installation

- All the `code` required to get started
- Images of what it should look like

### Clone

- Clone this repo to your local machine

### Setup

- If you want more syntax highlighting, format your code like this:

> Install postgresql and create a new database with:

```shell
$ createdb pre-registration
```

> create environment variables

```shell
$ export DATABASE_URL=postgresql://127.0.0.1/card_api_db
$ export FLASK_ENV=production
```
if you want to run in development configuration change FLASK_ENV=development

> Create a virtualenv with Python 3:

```shell
$ virtualenv -p python3 venv3
$ source venv3/bin/activate
```

> Install the requirements using requirements.txt

```shell
$ pip install -r requirements.txt
```

> Run the database migrations

```shell
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```

> Run the server
```shell
$ python run.py
```
The server should now be up and running!

## Examples

> You can try it out using the host: https://prepaidcard.herokuapp.com/

Note all parameters are required

> Get all cards: `GET /api/v1/cards/`

> Create a card `POST /api/v1/cards/`
```json
{"name": "Mickey Mouse", "card_nbr": "123456" }
```

> Get one cards: `GET /api/v1/cards/<id>`

> Get all transactions for a cards: `GET /api/v1/cards/<id>/transactions`

> Delete one card `DELETE /api/v1/cards/<id>`

> Top up a card `POST /api/v1/cards/topup`
```json
{"amount": 100 }
```

> Get all Merchants `GET /api/v1/merchants/`

> Create Merchant `POST /api/v1/merchants/`
```json
{"name": "The Frying Scottsman" }
```

> Get one Merchant: `GET /api/v1/merchants/<id>`

> Delete one Merchant `DELETE /api/v1/merchants/<id>`

> Authorization request of a card `POST /api/v1/merchants/<id>/auth_request`
```json
{"card_nbr": "123456", "amount": 50 }
```

> Capture `POST /api/v1/merchants/<id>/capture`
```json
{"transactions_id": 1, "amount": 50 }
```

> Reverse `POST /api/v1/merchants/<id>/reverse`
```json
{"transactions_id": 1, "amount": 50 }
```

> Refund `POST /api/v1/merchants/<id>/refund`
```json
{"card_nbr": "123456", "amount": 50 }
```
## Tests
> To run the tests:
> Create a new test data base in postgresql and new environment variables
```shell
$ export TEST_DATABASE_URL=postgresql://127.0.0.1/card_api_db_test
$ export FLASK_ENV=production
```
> In the src folder run:
```shell
$ python tests/tests.py
```
---