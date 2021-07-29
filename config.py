"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    """Base config."""
    SECRET_KEY = environ.get('SECRET_KEY')
    FLASK_ENV = 'development'
    FLASK_APP = 'app'
    DATABASE_URI = environ.get('DATABASE_URI')
    # DATABASE_URI = 'db'
    DATABASE_USER = environ.get('DATABASE_PASSWORD')
    DATABASE_NAME = environ.get('DATABASE_NAME')
    DATABASE_PORT = environ.get('DATABASE_PORT')
    DATABASE_USER = environ.get('DATABASE_USER')
    
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    # print(f'SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}')

class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True