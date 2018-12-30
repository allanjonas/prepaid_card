# /src/config.py

import os

class Development():
  """
  Development environment configuration
  """
  DEBUG = True
  TESTING = False
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class Production():
  """
  Production environment configurations
  """
  DEBUG = False
  TESTING = False
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

app_config = {
    'development': Development,
    'production': Production,
}
