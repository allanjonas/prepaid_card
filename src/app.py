from flask import Flask

from .config import app_config
from .models import db
from .views.CardView import card_api as card_blueprint
from .views.MerchantView import merchant_api as merchant_blueprint

def create_app(env_name):
  """
  Create app
  """
  # app initiliazation
  app = Flask(__name__)

  app.config.from_object(app_config[env_name])
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  db.init_app(app)

  app.register_blueprint(card_blueprint, url_prefix='/api/v1/cards')
  app.register_blueprint(merchant_blueprint, url_prefix='/api/v1/merchants')

  return app
