import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this_should_be_random'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'database', 'polylingua.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

