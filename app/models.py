import datetime
import jwt
from flask import current_app
from .extensions import db

class Game(db.Model):
    # __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'))

class Theme(db.Model):
    # __tablename__ = 'theme'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String, unique=True, nullable=False)
    games = db.relationship('Game', backref='theme', lazy=True)

    def __init__(self, name, title):
        self.name = name
        self.title = title

    def __repr__(self):
        return '<Theme %r>' % self.name

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
        }

class User(db.Model):
    # __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String, unique=True)
    email = db.Column(db.String(254), unique=True)
    username = db.Column(db.String, unique=True)
    photoURL = db.Column(db.String)
    providerId = db.Column(db.String)
    games = db.relationship('Game', backref='user', lazy=True)


    def __init__(self, uid, providerId, photoURL, username, email):
        self.uid = uid
        self.providerId = providerId
        self.photoURL = photoURL
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id,
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e


    def to_json(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'email': self.email,
            'photoURL': self.photoURL,
            'username': self.username,
        }


    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            # print(f'auth_token => {auth_token}')
            payload = jwt.decode(
                auth_token,
                options={"verify_signature": False},
            )
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

